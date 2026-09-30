"""remove server-side timestamp defaults, app sets UTC explicitly

Revision ID: a9c17bc21cfc
Revises: 13952a173f20
Create Date: 2026-09-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9c17bc21cfc'
down_revision: Union[str, None] = '13952a173f20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CREATED_AT_TABLES = ["departments", "users", "tickets", "ticket_messages", "assets"]
UPDATED_AT_TABLES = ["departments", "users", "tickets", "assets"]


def upgrade() -> None:
    for table in CREATED_AT_TABLES:
        op.alter_column(
            table,
            "created_at",
            existing_type=sa.DateTime(),
            server_default=None,
            existing_nullable=False,
        )
    for table in UPDATED_AT_TABLES:
        op.alter_column(
            table,
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=None,
            existing_nullable=False,
        )


def downgrade() -> None:
    for table in CREATED_AT_TABLES:
        op.alter_column(
            table,
            "created_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            existing_nullable=False,
        )
    for table in UPDATED_AT_TABLES:
        op.alter_column(
            table,
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            existing_nullable=False,
        )
