"""insert default roles

Revision ID: d5eaa4e9d714
Revises: 2e9cd2bb4f32
Create Date: 2026-07-08 11:51:00.528961

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5eaa4e9d714"
down_revision: str | Sequence[str] | None = "2e9cd2bb4f32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.bulk_insert(
        sa.table(
            "role",
            sa.column("id", sa.Integer),
            sa.column("name", sa.String),
        ),
        [
            {"id": 1, "name": "management"},
            {"id": 2, "name": "sales"},
            {"id": 3, "name": "support"},
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM role
        WHERE name IN ('management', 'sales', 'support')
        """
    )
