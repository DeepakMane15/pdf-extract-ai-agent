"""Simulated email send (no SMTP); admin-only."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.tools.base import BaseTool
from app.tools.context import ToolContext


class SendEmailInput(BaseModel):
    to: EmailStr
    subject: str = Field(..., max_length=500)
    body: str = Field(..., max_length=50_000)


class SendEmailTool(BaseTool):
    name: ClassVar[str] = 'send_email'
    description: ClassVar[str] = 'Simulate sending an email (dry-run; does not contact SMTP).'
    allowed_roles: ClassVar[frozenset[UserRole]] = frozenset({UserRole.admin})

    @classmethod
    def input_model(cls) -> type[BaseModel]:
        return SendEmailInput

    def execute(self, ctx: ToolContext, inputs: BaseModel) -> Any:
        data = inputs if isinstance(inputs, SendEmailInput) else SendEmailInput.model_validate(inputs)
        return {
            'simulated': True,
            'to': data.to,
            'subject': data.subject,
            'body_preview': data.body[:200] + ('…' if len(data.body) > 200 else ''),
            'requested_by': ctx.user.email,
        }
