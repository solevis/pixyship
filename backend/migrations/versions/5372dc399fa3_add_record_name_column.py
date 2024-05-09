"""Add Record name column

Revision ID: 5372dc399fa3
Revises: 6f6fcebc52f2
Create Date: 2024-04-28 19:03:42.523026

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5372dc399fa3"
down_revision = "6f6fcebc52f2"
branch_labels = None
depends_on = None


def upgrade():
    # add name column to record table
    op.add_column("record", sa.Column("name", sa.String(), nullable=True))


def downgrade():
    # remove name column from record table
    op.drop_column("record", "name")
