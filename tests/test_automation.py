from app.automation.engine import AutomationEngine
from app.automation.models import Action, AutomationRule, Condition


def test_rule_matches_and_runs_only_registered_action():
    calls = []
    engine = AutomationEngine({"notify": lambda event, params: calls.append((event, params))})
    rule = AutomationRule(id="quiet-hours", name="Notify owner", trigger="message.received",
        conditions=[Condition(field="chat.type", operator="eq", value="private")],
        actions=[Action(type="notify", params={"message": "New DM"})])
    result = engine.run(rule, "message.received", {"chat": {"type": "private"}})
    assert result.matched is True
    assert result.executed_actions == ["notify"]
    assert len(calls) == 1


def test_rule_does_not_match_wrong_trigger_or_condition():
    engine = AutomationEngine()
    rule = AutomationRule(id="r1", name="Draft", trigger="message.received",
        conditions=[Condition(field="sender.id", operator="eq", value=7)],
        actions=[Action(type="draft_reply")])
    assert not engine.run(rule, "profile.changed", {"sender": {"id": 7}}).matched
    assert not engine.run(rule, "message.received", {"sender": {"id": 8}}).matched


def test_missing_handler_is_reported_without_crashing():
    engine = AutomationEngine()
    rule = AutomationRule(id="r2", name="Snapshot", trigger="profile.changed", actions=[Action(type="snapshot")])
    result = engine.run(rule, "profile.changed", {})
    assert result.matched
    assert result.errors == ["No handler registered for action: snapshot"]


def test_rule_rejects_unknown_fields():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        AutomationRule(id="r3", name="bad", trigger="message.received", actions=[{"type": "notify"}], arbitrary_code="print(1)")
