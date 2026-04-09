import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, enum.Enum):
    admin = 'admin'
    user = 'user'
    auditor = 'auditor'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name='user_role'), default=UserRole.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    openai_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    openai_key_hint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    openai_embed_prompt_tokens_total: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        server_default='0',
        default=0,
    )
    openai_chat_prompt_tokens_total: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        server_default='0',
        default=0,
    )
    openai_chat_completion_tokens_total: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        server_default='0',
        default=0,
    )

    tool_logs = relationship('ToolExecutionLog', back_populates='user')
    uploaded_pdfs = relationship('PdfDocument', back_populates='uploaded_by')
