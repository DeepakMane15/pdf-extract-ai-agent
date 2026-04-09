"""Placeholder compliance screening on free text."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from app.models.user import UserRole
from app.tools.base import BaseTool
from app.tools.context import ToolContext


class ComplianceCheckInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=50_000)
    policy_hint: str | None = Field(None, max_length=200)


class ComplianceTool(BaseTool):
    name: ClassVar[str] = 'compliance_check'
    description: ClassVar[str] = 'Run a lightweight heuristic check on text (demo; not legal advice).'
    allowed_roles: ClassVar[frozenset[UserRole]] = frozenset({UserRole.admin, UserRole.auditor})

    @classmethod
    def input_model(cls) -> type[BaseModel]:
        return ComplianceCheckInput

    def execute(self, _ctx: ToolContext, inputs: BaseModel) -> Any:
        data = inputs if isinstance(inputs, ComplianceCheckInput) else ComplianceCheckInput.model_validate(inputs)
        lowered = data.text.lower()
        flags: list[str] = []
        for needle in ('password', 'ssn', 'credit card', 'confidential'):
            if needle in lowered:
                flags.append(needle)
        return {
            'review_required': len(flags) > 0,
            'matched_keywords': flags,
            'char_count': len(data.text),
            'policy_hint': data.policy_hint,
        }
