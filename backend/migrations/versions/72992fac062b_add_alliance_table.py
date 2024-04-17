"""Add Alliance table

Revision ID: 72992fac062b
Revises: e98016f3cfec
Create Date: 2018-12-19 22:26:31.370744

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "72992fac062b"
down_revision = "e98016f3cfec"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "alliance",
        sa.Column("id", sa.INT, primary_key=True),
        sa.Column("name", sa.TEXT, nullable=False),
        sa.Column("sprite_id", sa.INT, nullable=False),
    )


def downgrade():
    op.drop_table("alliance")
