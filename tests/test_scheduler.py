import pytest
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
    with pytest.raises(ValueError): store.due("2026-10-26T00:00:00Z", 0)
    with pytest.raises(ValueError): store.set_status("missing", "unknown")
