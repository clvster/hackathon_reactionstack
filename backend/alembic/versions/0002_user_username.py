"""add username to users, make email optional

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-11

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем username как nullable, чтобы не упасть на уже существующих
    # строках, бэкфилим значением по умолчанию, и только потом делаем
    # обязательным и уникальным.
    op.add_column(
        "users",
        sa.Column("username", sa.String(length=64), nullable=True),
    )
    op.execute("UPDATE users SET username = 'user_' || id WHERE username IS NULL")
    op.alter_column("users", "username", nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # email больше не используется для входа — делаем его опциональным
    # полем профиля.
    op.alter_column("users", "email", nullable=True)


def downgrade() -> None:
    op.alter_column("users", "email", nullable=False)
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
