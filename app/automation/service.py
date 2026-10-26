"""Orchestrate rule execution and write a redacted audit event."""
from typing import Any
from app.automation.engine import AutomationEngine
from app.automation.models import AutomationResult, AutomationRule
from app.security.audit import AuditLog

class AutomationService:
    def __init__(self, engine: AutomationEngine, audit_log: AuditLog):
        self.engine = engine
        self.audit_log = audit_log

    def handle_event(self, rule: AutomationRule, event_type: str, payload: dict[str, Any], *, actor: str = "system") -> AutomationResult:
        result = self.engine.run(rule, event_type, payload)
        if not result.matched:
            return result
        outcome = "partial_failure" if result.errors else "success"
        self.audit_log.record(
            actor=actor,
            action="automation.execute",
            outcome=outcome,
            resource_id=rule.id,
            details={"trigger": event_type, "executed_actions": result.executed_actions,
                     "errors": result.errors},
        )
        return result
