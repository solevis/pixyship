"""Change char to character in record.type

Revision ID: 7b4cf67136ba
Revises: 6f6fcebc52f2
Create Date: 2024-04-23 23:44:19.691918

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7b4cf67136ba'
down_revision = 'f6650357d5d8'
branch_labels = None
depends_on = None


def upgrade():
    # Convert record.type values to uppercase
    op.execute("UPDATE record SET type = 'character' WHERE type = 'char'")


def downgrade():
    # Convert record.type values to lowercase
    op.execute("UPDATE record SET type = 'char' WHERE type = 'character'")
