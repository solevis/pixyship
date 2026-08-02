"""Market pusher worker nullable columns

Revision ID: 300d9dd46169
Revises: c6df405d0ab3
Create Date: 2026-08-02 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "300d9dd46169"
down_revision = "c6df405d0ab3"
branch_labels = None
depends_on = None


def upgrade():
    # the market pusher worker only knows one side of a sale (either the buyer or the seller),
    # so the other side can't be filled anymore
    op.alter_column("listing", "user_id", existing_type=sa.INT, nullable=True)
    op.alter_column("listing", "user_name", existing_type=sa.TEXT, nullable=True)
    op.alter_column("listing", "seller_id", existing_type=sa.INT, nullable=True)
    op.alter_column("listing", "seller_name", existing_type=sa.TEXT, nullable=True)

    # the market pusher worker can fail to resolve the item from the message free text
    op.alter_column("market_message", "item_id", existing_type=sa.INT, nullable=True)


def downgrade():
    op.alter_column("market_message", "item_id", existing_type=sa.INT, nullable=False)

    op.alter_column("listing", "seller_name", existing_type=sa.TEXT, nullable=False)
    op.alter_column("listing", "seller_id", existing_type=sa.INT, nullable=False)
    op.alter_column("listing", "user_name", existing_type=sa.TEXT, nullable=False)
    op.alter_column("listing", "user_id", existing_type=sa.INT, nullable=False)
