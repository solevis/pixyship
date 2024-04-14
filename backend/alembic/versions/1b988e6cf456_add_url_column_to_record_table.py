"""Add URL column to record table

Revision ID: 1b988e6cf456
Revises: 2ce3dfcb486e
Create Date: 2022-06-09 20:47:51.927449

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1b988e6cf456"
down_revision = "2ce3dfcb486e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("record", sa.Column("url", sa.TEXT))


def downgrade():
    op.drop_column("record", "url")
