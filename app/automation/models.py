"""Typed models for declarative automation rules; no executable user code."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

TriggerType = Literal["message.received", "profile.changed", "message.deleted", "schedule.tick"]
ConditionOperator = Literal["eq", "neq", "contains", "in", "gte", "lte"]
ActionType = Literal["notify", "mark_read", "draft_reply", "snapshot"]

class Condition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z][a-zA-Z0-9_.]*$")
    operator: ConditionOperator
    value: Any = None

class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: ActionType
    params: dict[str, Any] = Field(default_factory=dict)

class AutomationRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(min_length=1, max_length=120)
    enabled: bool = True
    trigger: TriggerType
    conditions: list[Condition] = Field(default_factory=list, max_length=20)
    actions: list[Action] = Field(min_length=1, max_length=10)

class AutomationResult(BaseModel):
    rule_id: str
    matched: bool
    executed_actions: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
