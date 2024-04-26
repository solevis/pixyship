"""Change record.type column from text to Enum

Revision ID: 6f6fcebc52f2
Revises: ad2529eaf52f
Create Date: 2024-04-23 23:36:12.240436

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6f6fcebc52f2"
down_revision = "ed521b4cb886"
branch_labels = None
depends_on = None


def upgrade():
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
        name="type_enum",
    )
    type_enum.create(op.get_bind(), checkfirst=False)

    op.alter_column(
        "record",
        "type",
        existing_type=sa.Text(),
        type_=type_enum,
        existing_nullable=True,
        postgresql_using="type::text::type_enum",
    )


def downgrade():
    op.alter_column(
        "record",
        "type",
        existing_type=sa.Enum(name="type_enum"),
        type_=sa.Text(),
        existing_nullable=True,
        postgresql_using="type::text",
    )

    sa.Enum(name="type_enum").drop(op.get_bind(), checkfirst=False)
