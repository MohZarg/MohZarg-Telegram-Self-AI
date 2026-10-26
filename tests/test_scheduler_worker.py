from datetime import datetime, timezone

import pytest

from app.scheduler.store import JobStore
from app.scheduler.worker import JobWorker


NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def test_worker_runs_only_registered_handler_and_completes(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    calls = []
    store.enqueue("job-1", "2026-10-26T12:00:00Z", "notify", {"text": "hello"})
    worker = JobWorker(store, {"notify": lambda payload: calls.append(payload)})

    result = worker.run_once(now=NOW)

    assert result == {"claimed": 1, "completed": 1, "retried": 0, "failed": 0, "recovered": 0, "stale_failed": 0}
    assert calls == [{"text": "hello"}]
    assert store.due("2026-10-27T00:00:00Z") == []


def test_worker_retries_transient_handler_failure_without_leaking_message(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    store.enqueue("job-1", "2026-10-26T12:00:00Z", "notify", {"text": "private content"})

    def fail(_payload):
        raise RuntimeError("private content and token=secret")

    worker = JobWorker(store, {"notify": fail}, max_attempts=2)
    result = worker.run_once(now=NOW)
    assert result == {"claimed": 1, "completed": 0, "retried": 1, "failed": 0, "recovered": 0, "stale_failed": 0}

    claimed = store.claim_due("2026-10-26T12:00:01Z")
    assert claimed == []
    claimed = store.claim_due("2026-10-26T12:00:02Z")
    assert len(claimed) == 1
    assert claimed[0]["attempts"] == 2
    assert store.fail("job-1", "RuntimeError", max_attempts=2)
    assert store.due("2026-10-27T00:00:00Z") == []


def test_worker_marks_missing_handler_failed(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    store.enqueue("job-1", "2026-10-26T12:00:00Z", "unknown", {})
    worker = JobWorker(store, {})
    result = worker.run_once(now=NOW)
    assert result == {"claimed": 1, "completed": 0, "retried": 0, "failed": 1, "recovered": 0, "stale_failed": 0}


def test_worker_rejects_naive_clock_and_invalid_limits(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    with pytest.raises(ValueError, match="max_attempts"):
        JobWorker(store, {}, max_attempts=0)
    worker = JobWorker(store, {})
    with pytest.raises(ValueError, match="timezone-aware"):
        worker.run_once(now=datetime(2026, 10, 26, 12, 0))



def test_worker_recovers_expired_lease_before_claiming(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    calls = []
    store.enqueue("old-job", "2026-10-26T12:00:00Z", "notify", {"text": "once more"})
    store.claim_due("2026-10-26T12:00:00Z")

    worker = JobWorker(store, {"notify": lambda payload: calls.append(payload)})
    result = worker.run_once(now=datetime(2026, 10, 26, 12, 6, tzinfo=timezone.utc))

    assert result == {
        "claimed": 1, "completed": 1, "retried": 0, "failed": 0,
        "recovered": 1, "stale_failed": 0,
    }
    assert calls == [{"text": "once more"}]
