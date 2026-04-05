"""Add users table

Revision ID: 20260315_01
Revises:
Create Date: 2026-03-15 06:40:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260315_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _has_index(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    if not _has_table(bind, "incidents"):
        op.create_table(
            "incidents",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("location", sa.String(length=255), nullable=False),
            sa.Column(
                "status",
                sa.Enum("NEW", "IN_PROGRESS", "RESOLVED", "CANCELLED", name="incidentstatus"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_incidents_id", "incidents", ["id"], unique=False)

    if not _has_table(bind, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(length=100), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_index(bind, "users", "ix_users_id"):
        op.create_index("ix_users_id", "users", ["id"], unique=False)
    if not _has_index(bind, "users", "ix_users_username"):
        op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    if _has_table(bind, "users"):
        if _has_index(bind, "users", "ix_users_username"):
            op.drop_index("ix_users_username", table_name="users")
        if _has_index(bind, "users", "ix_users_id"):
            op.drop_index("ix_users_id", table_name="users")
        op.drop_table("users")
