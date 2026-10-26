"""Small synchronous scheduler worker with explicit handlers and bounded retry policy.

Handlers must be idempotent where possible. This worker never executes arbitrary payload code
and does not contain Telegram-specific behavior; integrations register narrowly scoped handlers.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
import logging
import threading
from typing import Any

from app.scheduler.store import JobStore

JobHandler = Callable[[dict[str, Any]], None]


class JobWorker:
    def __init__(
        self,
        store: JobStore,
        handlers: Mapping[str, JobHandler],
        *,
        max_attempts: int = 3,
        batch_size: int = 25,
        audit_log: Any | None = None,
    ):
        if not 1 <= max_attempts <= 20:
            raise ValueError("max_attempts must be between 1 and 20")
        if not 1 <= batch_size <= 500:
            raise ValueError("batch_size must be between 1 and 500")
        self.store = store
        self.handlers = dict(handlers)
        self.max_attempts = max_attempts
        self.batch_size = batch_size
        self.audit_log = audit_log

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def _audit(self, job: dict[str, Any], outcome: str, error: str = "") -> None:
        if self.audit_log is None:
            return
        self.audit_log.record(
            actor="scheduler",
            action="scheduler.execute",
            outcome=outcome,
            resource_id=str(job["id"]),
            details={
                "job_type": job["job_type"],
                "attempt": job["attempts"],
                "error": error,
            },
        )

    def run_once(self, *, now: datetime | None = None) -> dict[str, int]:
        current = now or self._now()
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        now_iso = current.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
        recovery = self.store.recover_stale(now_iso, max_attempts=self.max_attempts)
        jobs = self.store.claim_due(now_iso, self.batch_size)
        summary = {
            "claimed": len(jobs), "completed": 0, "retried": 0, "failed": 0,
            "recovered": recovery["requeued"], "stale_failed": recovery["failed"],
        }
        for job in jobs:
            handler = self.handlers.get(job["job_type"])
            if handler is None:
                error = "NoHandlerRegistered"
                self.store.fail(job["id"], error, max_attempts=self.max_attempts)
                summary["failed"] += 1
                self._audit(job, "failed", error)
                continue
            try:
                handler(dict(job["payload"]))
                if self.store.complete(job["id"]):
                    summary["completed"] += 1
                    self._audit(job, "success")
            except Exception as exc:
                # Never persist exception messages: they can contain payloads or credentials.
                error = type(exc).__name__
                delay_seconds = min(2 ** int(job["attempts"]), 300)
                retry_at = (current + timedelta(seconds=delay_seconds)).isoformat(
                    timespec="microseconds"
                ).replace("+00:00", "Z")
                retry = int(job["attempts"]) < self.max_attempts
                self.store.fail(
                    job["id"], error,
                    retry_at=retry_at if retry else None,
                    max_attempts=self.max_attempts,
                )
                summary["retried" if retry else "failed"] += 1
                self._audit(job, "retry" if retry else "failed", error)
        return summary

    def run_forever(self, stop_event: threading.Event, *, poll_interval: float = 1.0) -> None:
        if not 0.1 <= poll_interval <= 60:
            raise ValueError("poll_interval must be between 0.1 and 60 seconds")
        while not stop_event.is_set():
            try:
                self.run_once()
            except Exception as exc:
                # Log the exception type only; exception text can contain payloads or secrets.
                logging.getLogger(__name__).error(
                    "scheduler iteration failed (%s)", type(exc).__name__
                )
            stop_event.wait(poll_interval)
