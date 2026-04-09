from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel

from app.models.user import UserRole
from app.tools.context import ToolContext


class BaseTool(ABC):
    """Registered tool: Pydantic input, execute(), and role gate."""

    name: ClassVar[str]
    description: ClassVar[str]
    allowed_roles: ClassVar[frozenset[UserRole]]

    @classmethod
    @abstractmethod
    def input_model(cls) -> type[BaseModel]:
        """Pydantic model for `arguments` JSON."""

    @abstractmethod
    def execute(self, ctx: ToolContext, inputs: BaseModel) -> Any:
        """Run the tool; return JSON-serializable result or str."""

    def validate_inputs(self, raw: dict[str, Any]) -> BaseModel:
        return self.input_model().model_validate(raw)
