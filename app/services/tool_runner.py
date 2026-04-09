"""Execute registered tools with RBAC, timing, and persistence of execution logs."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from sqlalchemy.orm import Session

from app.models.tool_execution_log import ToolExecutionLog
from app.models.user import User
from app.tools.context import ToolContext
from app.tools.registry import get_tool


class ToolRunCode(str, Enum):
    ok = 'ok'
    unknown_tool = 'unknown_tool'
    forbidden = 'forbidden'
    validation_error = 'validation_error'
    execution_error = 'execution_error'


@dataclass
class ToolRunResult:
    code: ToolRunCode
    success: bool
    output: Any | None
    error: str | None
    duration_ms: int
    log_id: int


def _serialize_output(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except TypeError:
        return repr(value)


def run_tool(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    db: Session,
    user: User,
) -> ToolRunResult:
    tool = get_tool(tool_name)
    if tool is None:
        log = ToolExecutionLog(
            tool_name=tool_name,
            input_args=arguments,
            output_text=None,
            duration_ms=0,
            success=False,
            error_message='Unknown tool',
            user_id=user.id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return ToolRunResult(ToolRunCode.unknown_tool, False, None, 'Unknown tool', 0, log.id)

    if user.role not in tool.allowed_roles:
        log = ToolExecutionLog(
            tool_name=tool_name,
            input_args=arguments,
            output_text=None,
            duration_ms=0,
            success=False,
            error_message='Forbidden: role not allowed for this tool',
            user_id=user.id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return ToolRunResult(ToolRunCode.forbidden, False, None, log.error_message, 0, log.id)

    try:
        validated = tool.validate_inputs(arguments)
    except Exception as exc:  # noqa: BLE001 — log validation failures
        log = ToolExecutionLog(
            tool_name=tool_name,
            input_args=arguments,
            output_text=None,
            duration_ms=0,
            success=False,
            error_message=f'Invalid arguments: {exc}',
            user_id=user.id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return ToolRunResult(ToolRunCode.validation_error, False, None, log.error_message, 0, log.id)

    ctx = ToolContext(db=db, user=user)
    t0 = time.perf_counter()
    try:
        out = tool.execute(ctx, validated)
        duration_ms = int((time.perf_counter() - t0) * 1000)
        log = ToolExecutionLog(
            tool_name=tool_name,
            input_args=arguments,
            output_text=_serialize_output(out),
            duration_ms=duration_ms,
            success=True,
            error_message=None,
            user_id=user.id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return ToolRunResult(ToolRunCode.ok, True, out, None, duration_ms, log.id)
    except Exception as exc:  # noqa: BLE001 — persist tool/runtime errors
        duration_ms = int((time.perf_counter() - t0) * 1000)
        err = str(exc)
        log = ToolExecutionLog(
            tool_name=tool_name,
            input_args=arguments,
            output_text=None,
            duration_ms=duration_ms,
            success=False,
            error_message=err,
            user_id=user.id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return ToolRunResult(ToolRunCode.execution_error, False, None, err, duration_ms, log.id)
