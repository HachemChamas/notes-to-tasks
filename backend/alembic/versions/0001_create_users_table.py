"""Create the users table.

Revision ID: 0001
Revises: (none, this is the first migration)

A migration is a small script that changes the database step by step.
`upgrade()` applies the change and `downgrade()` undoes it.
Alembic remembers which migrations already ran in a table called
`alembic_version`, so each one only runs once.
"""

import sqlalchemy as sa
from alembic import op

# Alembic uses these two IDs to put migrations in order.
revision = "0001"
down_revision = None  # None means "this is the first migration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep these columns in sync with the User model in app/models.py.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
