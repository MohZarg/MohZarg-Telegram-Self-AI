from app.automation.engine import AutomationEngine
from app.automation.models import Action, AutomationRule
from app.automation.service import AutomationService
from app.security.audit import AuditLog


def test_service_audits_matched_rule_without_logging_message_body(tmp_path):
    audit = AuditLog(tmp_path / "audit.sqlite3")
    engine = AutomationEngine({"notify": lambda payload, params: None})
    service = AutomationService(engine, audit)
    rule = AutomationRule(id="dm-rule", name="DM notice", trigger="message.received", actions=[Action(type="notify")])
    service.handle_event(rule, "message.received", {"message": "private user text"})
    event = audit.recent()[0]
    assert event["action"] == "automation.execute"
    assert event["resource_id"] == "dm-rule"
    assert "private user text" not in str(event)


def test_service_does_not_audit_unmatched_event(tmp_path):
    audit = AuditLog(tmp_path / "audit.sqlite3")
    service = AutomationService(AutomationEngine(), audit)
    rule = AutomationRule(id="profile-rule", name="Profile", trigger="profile.changed", actions=[Action(type="snapshot")])
    service.handle_event(rule, "message.received", {})
    assert audit.recent() == []
