"""Login and token tracking

Revision ID: bdc90a07b024
Revises: cf08232a3b60
Create Date: 2018-06-02 19:41:58.999113

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bdc90a07b024"
down_revision = "cf08232a3b60"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "device",
        sa.Column("key", sa.TEXT, primary_key=True),
        sa.Column("checksum", sa.TEXT, nullable=False),
        sa.Column("token", sa.TEXT),
        sa.Column("expires_at", sa.TIMESTAMP),
    )


def downgrade():
    op.drop_table("device")
