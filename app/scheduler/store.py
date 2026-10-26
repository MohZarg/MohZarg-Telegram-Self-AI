"""SQLite-backed one-shot job store. A worker/cron loop is intentionally separate."""
import json
import sqlite3
from pathlib import Path
from typing import Any

class JobStore:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS scheduled_jobs (
                id TEXT PRIMARY KEY, run_at TEXT NOT NULL, job_type TEXT NOT NULL,
                payload_json TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_due ON scheduled_jobs(status, run_at)")

    def _connect(self):
        db = sqlite3.connect(self.database_path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def enqueue(self, job_id: str, run_at: str, job_type: str, payload: dict[str, Any]) -> None:
        if not job_id or not job_type or len(job_id) > 100 or len(job_type) > 80:
            raise ValueError("Invalid job id or type")
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        with self._connect() as db:
            db.execute("INSERT INTO scheduled_jobs(id, run_at, job_type, payload_json) VALUES(?,?,?,?)",
                       (job_id, run_at, job_type, encoded))

    def due(self, now_iso: str, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        with self._connect() as db:
            rows = db.execute("SELECT * FROM scheduled_jobs WHERE status='pending' AND run_at<=? ORDER BY run_at LIMIT ?",
                              (now_iso, limit)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json"))
            result.append(item)
        return result

    def set_status(self, job_id: str, status: str) -> bool:
        if status not in {"pending", "running", "completed", "failed", "cancelled"}:
            raise ValueError("Invalid job status")
        with self._connect() as db:
            cur = db.execute("UPDATE scheduled_jobs SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                             (status, job_id))
            return cur.rowcount == 1
