"""Add Record sprite_id column

Revision ID: c4510c3c0cda
Revises: 5372dc399fa3
Create Date: 2024-04-28 23:36:42.002327

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c4510c3c0cda"
down_revision = "5372dc399fa3"
branch_labels = None
depends_on = None


def upgrade():
    # add sprite_id column to record table
    op.add_column("record", sa.Column("sprite_id", sa.Integer(), nullable=True))


def downgrade():
    # remove sprite_id column from record table
    op.drop_column("record", "sprite_id")
