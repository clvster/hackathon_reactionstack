from typing import Optional
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Логин пользователя в системе. Обязательный, уникальный.
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Email — теперь необязательное поле профиля, не используется для входа.
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False)  # BACK, FRONT, QA
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )