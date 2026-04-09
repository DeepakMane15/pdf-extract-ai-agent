from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolInvokeRequest(BaseModel):
    tool_name: str = Field(..., min_length=1, max_length=128)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolInvokeResponse(BaseModel):
    success: bool
    output: Any | None = None
    error: str | None = None
    duration_ms: int
    log_id: int
