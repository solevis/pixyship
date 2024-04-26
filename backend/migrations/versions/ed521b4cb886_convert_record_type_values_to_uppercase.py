"""Convert record.type values to uppercase

Revision ID: ed521b4cb886
Revises: 6f6fcebc52f2
Create Date: 2024-04-26 15:51:09.752840

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "ed521b4cb886"
down_revision = "7b4cf67136ba"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE record SET type = UPPER(type)")


def downgrade():
    op.execute("UPDATE record SET type = LOWER(type)")
