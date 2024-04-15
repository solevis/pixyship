"""add market buyer and seller name

Revision ID: 02434df3f8fa
Revises: 6033f73dc5ea
Create Date: 2021-03-30 22:37:54.132117

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "02434df3f8fa"
down_revision = "6033f73dc5ea"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("listing", sa.Column("user_name", sa.TEXT))
    op.add_column("listing", sa.Column("seller_name", sa.TEXT))
    op.add_column("listing", sa.Column("seller_id", sa.INT))


def downgrade():
    op.drop_column("listing", "user_name")
    op.drop_column("listing", "seller_name")
    op.drop_column("listing", "seller_id")
