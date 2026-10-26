import pytest
from datetime import datetime, timezone
from app.scheduler.store import JobStore


def test_job_store_enqueue_due_and_status(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    store.enqueue("job-1", "2026-10-26T12:00:00Z", "notify", {"message": "hello"})
    assert store.due("2026-10-26T11:59:59Z") == []
    due = store.due("2026-10-26T12:00:00Z")
    assert due[0]["payload"] == {"message": "hello"}
    assert store.set_status("job-1", "completed")
    assert store.due("2026-10-27T12:00:00Z") == []


def test_job_store_validates_limits_and_status(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    with pytest.raises(ValueError):
        store.due("2026-10-26T00:00:00Z", 0)
    with pytest.raises(ValueError):
        store.set_status("missing", "unknown")


def test_job_store_requires_timezone_and_object_payload(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    with pytest.raises(ValueError, match="timezone"):
        store.enqueue("job-naive", "2026-10-26T12:00:00", "notify", {})
    with pytest.raises(ValueError, match="object"):
        store.enqueue("job-bad-payload", "2026-10-26T12:00:00Z", "notify", ["not", "an", "object"])


def test_claim_is_atomic_and_claimed_job_is_not_due_again(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    store.enqueue("job-1", "2026-10-26T12:00:00Z", "notify", {"message": "hello"})
    now = "2026-10-26T12:00:01Z"
    claimed = store.claim_due(now)
    assert len(claimed) == 1
    assert claimed[0]["status"] == "running"
    assert claimed[0]["attempts"] == 1
    assert store.claim_due(now) == []
    assert store.complete("job-1")
    assert not store.complete("job-1")


def test_failed_job_can_be_retried_then_terminally_failed(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    store.enqueue("job-1", "2026-10-26T12:00:00Z", "notify", {})
    claimed = store.claim_due("2026-10-26T12:00:00Z")[0]
    assert store.fail("job-1", "TimeoutError", retry_at="2026-10-26T12:00:02Z", max_attempts=2)
    assert store.due("2026-10-26T12:00:01Z") == []
    claimed = store.claim_due("2026-10-26T12:00:02Z")[0]
    assert claimed["attempts"] == 2
    assert store.fail("job-1", "TimeoutError", retry_at="2026-10-26T12:00:04Z", max_attempts=2)
    assert store.due("2026-10-27T00:00:00Z") == []
    assert store.set_status("job-1", "failed")


def test_timestamp_offsets_are_normalized_to_utc(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite3")
    store.enqueue("job-1", "2026-10-26T14:00:00+02:00", "notify", {})
    assert store.due("2026-10-26T12:00:00Z")[0]["id"] == "job-1"
