import json
import pytest
from app.security.audit import AuditLog, redact


def test_audit_redacts_sensitive_fields_and_persists(tmp_path):
    log = AuditLog(tmp_path / "audit.sqlite3")
    event_id = log.record(actor="owner", action="session.connect", outcome="denied",
                          resource_id="account-1", details={"reason": "permission", "bot_token": "123", "nested": {"session_data": "private"}})
    event = log.recent()[0]
    assert event["id"] == event_id
    assert event["details"]["bot_token"] == "[redacted]"
    assert event["details"]["nested"]["session_data"] == "[redacted]"
    assert "123" not in json.dumps(event)


def test_audit_validates_limit_and_required_fields(tmp_path):
    log = AuditLog(tmp_path / "audit.sqlite3")
    with pytest.raises(ValueError): log.recent(0)
    with pytest.raises(ValueError): log.record(actor="", action="x", outcome="ok")


def test_redact_bounds_nested_data():
    assert redact({"api_hash": "secret", "normal": "x"}) == {"api_hash": "[redacted]", "normal": "x"}
