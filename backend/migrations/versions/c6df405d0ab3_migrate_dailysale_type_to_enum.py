"""Migrate DailySale type to enum

Revision ID: c6df405d0ab3
Revises: c4510c3c0cda
Create Date: 2024-05-05 22:01:44.088732

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c6df405d0ab3"
down_revision = "c4510c3c0cda"
branch_labels = None
depends_on = None


def upgrade():
    # add new values to the type_enum
    op.execute("ALTER TYPE type_enum ADD VALUE 'FLEETGIFT'")
    op.execute("ALTER TYPE type_enum ADD VALUE 'NONE'")
    op.execute("ALTER TYPE type_enum ADD VALUE 'BONUS'")

    op.execute("COMMIT")

    op.execute("UPDATE daily_sale SET type = UPPER(type)")

    type_enum = sa.Enum(
        "ACHIEVEMENT",
        "CHARACTER",
        "COLLECTION",
        "CRAFT",
        "ITEM",
        "MISSILE",
        "PRESTIGE",
        "RESEARCH",
        "ROOM",
        "ROOM_SPRITE",
        "SHIP",
        "SKIN",
        "SKINSET",
        "SPRITE",
        "TRAINING",
        "FLEETGIFT",
        "NONE",
        "BONUS",
        name="type_enum",
    )

    op.alter_column(
        "daily_sale",
        "type",
        existing_type=sa.Text(),
        type_=type_enum,
        existing_nullable=True,
        postgresql_using="type::text::type_enum",
    )


def downgrade():
    op.alter_column(
        "daily_sale",
        "type",
        existing_type=sa.Enum(name="type_enum"),
        type_=sa.Text(),
        existing_nullable=True,
        postgresql_using="type::text",
    )

    op.execute("UPDATE daily_sale SET type = LOWER(type)")

    op.execute("ALTER TYPE type_enum DROP VALUE 'FLEETGIFT'")
    op.execute("ALTER TYPE type_enum DROP VALUE 'NONE'")
    op.execute("ALTER TYPE type_enum DROP VALUE 'BONUS'")
