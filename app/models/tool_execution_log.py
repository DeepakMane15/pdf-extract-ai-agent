from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ToolExecutionLog(Base):
    __tablename__ = 'tool_execution_logs'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    input_args: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship('User', back_populates='tool_logs')
