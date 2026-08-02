"""Add user_id to device

Revision ID: 7fe8603616c1
Revises: 300d9dd46169
Create Date: 2026-08-02 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7fe8603616c1"
down_revision = "300d9dd46169"
branch_labels = None
depends_on = None


def upgrade():
    # captured from DeviceLogin17's response so a device's identity can be reused to authorize a
    # long-lived Pusher connection (see the "market-worker" CLI command)
    op.add_column("device", sa.Column("user_id", sa.TEXT, nullable=True))


def downgrade():
    op.drop_column("device", "user_id")
