"""Small, deterministic automation engine with an explicit action allowlist.

This engine never executes Python supplied by a user and never sends Telegram messages
itself. Integrations must register policy-checked action handlers separately.
"""
from collections.abc import Callable, Mapping
from typing import Any
from app.automation.models import AutomationResult, AutomationRule, Condition

Handler = Callable[[dict[str, Any], dict[str, Any]], None]


def _field(payload: Mapping[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def condition_matches(condition: Condition, payload: Mapping[str, Any]) -> bool:
    actual = _field(payload, condition.field)
    expected = condition.value
    op = condition.operator
    if op == "eq": return actual == expected
    if op == "neq": return actual != expected
    if op == "contains": return isinstance(actual, (str, list, tuple, set)) and expected in actual
    if op == "in": return isinstance(expected, (list, tuple, set)) and actual in expected
    if op == "gte":
        try: return actual is not None and actual >= expected
        except TypeError: return False
    if op == "lte":
        try: return actual is not None and actual <= expected
        except TypeError: return False
    return False


class AutomationEngine:
    def __init__(self, handlers: Mapping[str, Handler] | None = None):
        self._handlers = dict(handlers or {})

    def register_handler(self, action_type: str, handler: Handler) -> None:
        if action_type not in {"notify", "mark_read", "draft_reply", "snapshot"}:
            raise ValueError("Action type is not allowlisted")
        self._handlers[action_type] = handler

    def run(self, rule: AutomationRule, event_type: str, payload: dict[str, Any]) -> AutomationResult:
        result = AutomationResult(rule_id=rule.id, matched=False)
        if not rule.enabled or rule.trigger != event_type:
            return result
        if not all(condition_matches(c, payload) for c in rule.conditions):
            return result
        result.matched = True
        for action in rule.actions:
            handler = self._handlers.get(action.type)
            if handler is None:
                result.errors.append(f"No handler registered for action: {action.type}")
                continue
            try:
                handler(dict(payload), dict(action.params))
                result.executed_actions.append(action.type)
            except Exception as exc:  # errors are deliberately reduced to type only
                result.errors.append(f"{action.type} failed ({type(exc).__name__})")
        return result
