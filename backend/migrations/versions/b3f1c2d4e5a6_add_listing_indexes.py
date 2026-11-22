"""Add listing indexes

Revision ID: b3f1c2d4e5a6
Revises: 7fe8603616c1
Create Date: 2026-11-17 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b3f1c2d4e5a6"
down_revision = "7fe8603616c1"
branch_labels = None
depends_on = None


def upgrade():
    # CONCURRENTLY can't run in a transaction, and avoids locking writes (market worker) on this big table
    with op.get_context().autocommit_block():
        # item price history and last players sales
        op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_listing_item_id_sale_at ON listing (item_id, sale_at)")
        # last sale id of an item, to only retrieve new sales during import
        op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_listing_item_id_id ON listing (item_id, id)")
        # market prices summary of the last 48 hours, for all items
        op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_listing_sale_at ON listing (sale_at)")


def downgrade():
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_listing_sale_at")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_listing_item_id_id")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_listing_item_id_sale_at")
