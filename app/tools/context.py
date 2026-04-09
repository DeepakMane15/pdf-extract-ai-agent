from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.user import User


@dataclass
class ToolContext:
    db: Session
    user: User
