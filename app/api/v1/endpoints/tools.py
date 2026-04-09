from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.tools import ToolInvokeRequest, ToolInvokeResponse
from app.services.tool_runner import ToolRunCode, run_tool
from app.tools.registry import list_tool_metadata

router = APIRouter()


@router.get('/tools', tags=['tools'])
def list_tools(_: User = Depends(get_current_user)) -> list[dict[str, object]]:
    """Discover registered tools, JSON Schemas, and allowed roles."""
    return list_tool_metadata()


@router.post('/tools/invoke', response_model=ToolInvokeResponse, tags=['tools'])
def invoke_tool(
    payload: ToolInvokeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ToolInvokeResponse:
    """Run a tool by name with JSON arguments; execution is logged."""
    result = run_tool(payload.tool_name, payload.arguments, db=db, user=user)
    if result.code is ToolRunCode.forbidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=result.error or 'Forbidden')
    return ToolInvokeResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        duration_ms=result.duration_ms,
        log_id=result.log_id,
    )
