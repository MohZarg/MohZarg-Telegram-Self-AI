"""Minimal SQLite audit trail with conservative secret redaction."""
import json
import sqlite3
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

_SENSITIVE = ("token", "secret", "password", "session", "api_hash", "authorization", "cookie", "key")

def redact(value: Any, depth: int = 0) -> Any:
    if depth > 8:
        return "[truncated]"
    if isinstance(value, dict):
        result = {}
        for key, item in list(value.items())[:100]:
            if any(part in str(key).lower() for part in _SENSITIVE):
                result[str(key)] = "[redacted]"
            else:
                result[str(key)] = redact(item, depth + 1)
        return result
    if isinstance(value, list):
        return [redact(item, depth + 1) for item in value[:100]]
    if isinstance(value, str):
        return value[:2000]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(type(value).__name__)

class AuditLog:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL,
                actor TEXT NOT NULL, action TEXT NOT NULL, outcome TEXT NOT NULL,
                resource_id TEXT, details_json TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_audit_occurred_at ON audit_events(occurred_at)")

    def _connect(self):
        db = sqlite3.connect(self.database_path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def record(self, *, actor: str, action: str, outcome: str,
               resource_id: str | None = None, details: dict[str, Any] | None = None) -> int:
        for name, value, maximum in (("actor", actor, 120), ("action", action, 120), ("outcome", outcome, 40)):
            if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                raise ValueError(f"Invalid {name}")
        details_json = json.dumps(redact(details or {}), ensure_ascii=False, separators=(",", ":"))
        occurred_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            cur = db.execute("INSERT INTO audit_events(occurred_at,actor,action,outcome,resource_id,details_json) VALUES(?,?,?,?,?,?)",
                              (occurred_at, actor, action, outcome, (resource_id or "")[:160], details_json))
            return int(cur.lastrowid)

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        with self._connect() as db:
            rows = db.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        events = []
        for row in rows:
            event = dict(row)
            event["details"] = json.loads(event.pop("details_json"))
            events.append(event)
        return events
