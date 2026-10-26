import sqlite3

import pytest

from app.scheduler.backup import backup_database, restore_database
from app.scheduler.store import JobStore


def test_backup_and_restore_preserve_scheduler_jobs(tmp_path):
    source = tmp_path / "source.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    store = JobStore(source)
    store.enqueue("job-1", "2026-10-26T12:00:00Z", "telegram_admin_message", {"text": "hello"})

    assert backup_database(source, backup) == backup
    assert restore_database(backup, restored) == restored
    restored_store = JobStore(restored)
    jobs = restored_store.due("2026-10-26T12:00:00Z")
    assert len(jobs) == 1
    assert jobs[0]["payload"] == {"text": "hello"}


def test_backup_refuses_overwrite_and_restore_requires_explicit_overwrite(tmp_path):
    source = tmp_path / "source.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    target = tmp_path / "target.sqlite3"
    JobStore(source)
    backup_database(source, backup)
    with pytest.raises(FileExistsError):
        backup_database(source, backup)
    JobStore(target)
    with pytest.raises(FileExistsError):
        restore_database(backup, target)
    assert restore_database(backup, target, overwrite=True) == target


def test_restore_rejects_corrupt_backup(tmp_path):
    corrupt = tmp_path / "corrupt.sqlite3"
    corrupt.write_text("not a sqlite database", encoding="utf-8")
    with pytest.raises(sqlite3.DatabaseError):
        restore_database(corrupt, tmp_path / "target.sqlite3")


def test_backup_requires_existing_source_and_distinct_paths(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(FileNotFoundError):
        backup_database(missing, tmp_path / "backup.sqlite3")
    source = tmp_path / "source.sqlite3"
    JobStore(source)
    with pytest.raises(ValueError, match="different paths"):
        backup_database(source, source)
