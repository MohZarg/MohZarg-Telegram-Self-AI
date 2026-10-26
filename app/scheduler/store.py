"""SQLite-backed durable job storage with atomic claiming and bounded retries."""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timedelta, timezone
import json
import sqlite3
from pathlib import Path
from typing import Any


def _utc_iso(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Timestamp must be a non-empty ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Timestamp must be valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class JobStore:
    """A small durable queue; claiming is transactional across competing workers."""

    VALID_STATUSES = {"pending", "running", "completed", "failed", "cancelled"}

    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db, db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    id TEXT PRIMARY KEY, run_at TEXT NOT NULL, job_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            columns = {row["name"] for row in db.execute("PRAGMA table_info(scheduled_jobs)")}
            # Forward-only, additive migration keeps existing local SQLite databases usable.
            if "attempts" not in columns:
                db.execute("ALTER TABLE scheduled_jobs ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0")
            if "locked_at" not in columns:
                db.execute("ALTER TABLE scheduled_jobs ADD COLUMN locked_at TEXT")
            if "last_error" not in columns:
                db.execute("ALTER TABLE scheduled_jobs ADD COLUMN last_error TEXT")
            db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_due ON scheduled_jobs(status, run_at)")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database_path, timeout=5, isolation_level="DEFERRED")
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=5000")
        return db

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json"))
        return item

    def enqueue(self, job_id: str, run_at: str, job_type: str, payload: dict[str, Any]) -> None:
        if not isinstance(job_id, str) or not job_id.strip() or len(job_id) > 100:
            raise ValueError("Invalid job id")
        if not isinstance(job_type, str) or not job_type.strip() or len(job_type) > 80:
            raise ValueError("Invalid job type")
        if not isinstance(payload, dict):
            raise ValueError("Job payload must be an object")
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        if len(encoded.encode("utf-8")) > 1_000_000:
            raise ValueError("Job payload exceeds 1 MB")
        with closing(self._connect()) as db, db:
            db.execute(
                "INSERT INTO scheduled_jobs(id, run_at, job_type, payload_json) VALUES(?,?,?,?)",
                (job_id.strip(), _utc_iso(run_at), job_type.strip(), encoded),
            )

    def due(self, now_iso: str, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        now = _utc_iso(now_iso)
        with closing(self._connect()) as db:
            rows = db.execute(
                """SELECT * FROM scheduled_jobs
                   WHERE status='pending' AND run_at<=?
                   ORDER BY run_at, created_at LIMIT ?""",
                (now, limit),
            ).fetchall()
        return [self._decode(row) for row in rows]

    def claim_due(self, now_iso: str, limit: int = 50) -> list[dict[str, Any]]:
        """Atomically transition due jobs to running, preventing duplicate worker claims."""
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        now = _utc_iso(now_iso)
        with closing(self._connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute(
                """SELECT id FROM scheduled_jobs
                   WHERE status='pending' AND run_at<=?
                   ORDER BY run_at, created_at LIMIT ?""",
                (now, limit),
            ).fetchall()
            ids = [row["id"] for row in rows]
            if not ids:
                return []
            placeholders = ",".join("?" for _ in ids)
            db.execute(
                f"""UPDATE scheduled_jobs
                    SET status='running', attempts=attempts+1, locked_at=?, updated_at=CURRENT_TIMESTAMP
                    WHERE status='pending' AND id IN ({placeholders})""",
                [now, *ids],
            )
            claimed = db.execute(
                f"SELECT * FROM scheduled_jobs WHERE status='running' AND id IN ({placeholders}) ORDER BY run_at, created_at",
                ids,
            ).fetchall()
            return [self._decode(row) for row in claimed]

    def recover_stale(
        self,
        now_iso: str,
        *,
        stale_after_seconds: int = 300,
        max_attempts: int = 3,
        limit: int = 100,
    ) -> dict[str, int]:
        """Recover expired worker leases transactionally.

        Requeued jobs provide at-least-once delivery; handlers must be idempotent because a
        process can crash after an external side effect but before marking the job complete.
        """
        if not 1 <= stale_after_seconds <= 86400:
            raise ValueError("stale_after_seconds must be between 1 and 86400")
        if not 1 <= max_attempts <= 20:
            raise ValueError("max_attempts must be between 1 and 20")
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        now = _utc_iso(now_iso)
        now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        cutoff = (now_dt - timedelta(seconds=stale_after_seconds)).isoformat(
            timespec="microseconds"
        ).replace("+00:00", "Z")
        counts = {"requeued": 0, "failed": 0}
        with closing(self._connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute(
                """SELECT id, attempts, locked_at FROM scheduled_jobs
                   WHERE status='running' AND locked_at IS NOT NULL AND locked_at<=?
                   ORDER BY locked_at LIMIT ?""",
                (cutoff, limit),
            ).fetchall()
            for row in rows:
                if int(row["attempts"]) < max_attempts:
                    cur = db.execute(
                        """UPDATE scheduled_jobs
                           SET status='pending', run_at=?, locked_at=NULL,
                               last_error='WorkerLeaseExpired', updated_at=CURRENT_TIMESTAMP
                           WHERE id=? AND status='running' AND locked_at=?""",
                        (now, row["id"], row["locked_at"]),
                    )
                    if cur.rowcount:
                        counts["requeued"] += 1
                else:
                    cur = db.execute(
                        """UPDATE scheduled_jobs
                           SET status='failed', locked_at=NULL,
                               last_error='WorkerLeaseExpired', updated_at=CURRENT_TIMESTAMP
                           WHERE id=? AND status='running' AND locked_at=?""",
                        (row["id"], row["locked_at"]),
                    )
                    if cur.rowcount:
                        counts["failed"] += 1
        return counts

    def set_status(self, job_id: str, status: str) -> bool:
        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid job status")
        with closing(self._connect()) as db, db:
            cur = db.execute(
                """UPDATE scheduled_jobs
                   SET status=?, locked_at=CASE WHEN ?='running' THEN locked_at ELSE NULL END,
                       updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                (status, status, job_id),
            )
            return cur.rowcount == 1

    def complete(self, job_id: str) -> bool:
        with closing(self._connect()) as db, db:
            cur = db.execute(
                """UPDATE scheduled_jobs SET status='completed', locked_at=NULL, last_error=NULL,
                   updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='running'""",
                (job_id,),
            )
            return cur.rowcount == 1

    def fail(self, job_id: str, error: str, *, retry_at: str | None = None,
             max_attempts: int = 3) -> bool:
        if not 1 <= max_attempts <= 20:
            raise ValueError("max_attempts must be between 1 and 20")
        safe_error = (error or "UnknownError")[:120]
        with closing(self._connect()) as db, db:
            row = db.execute(
                "SELECT attempts FROM scheduled_jobs WHERE id=? AND status='running'", (job_id,)
            ).fetchone()
            if row is None:
                return False
            retry = retry_at is not None and int(row["attempts"]) < max_attempts
            status = "pending" if retry else "failed"
            run_at = _utc_iso(retry_at) if retry else None
            cur = db.execute(
                """UPDATE scheduled_jobs SET status=?, run_at=COALESCE(?, run_at),
                   locked_at=NULL, last_error=?, updated_at=CURRENT_TIMESTAMP
                   WHERE id=? AND status='running'""",
                (status, run_at, safe_error, job_id),
            )
            return cur.rowcount == 1
