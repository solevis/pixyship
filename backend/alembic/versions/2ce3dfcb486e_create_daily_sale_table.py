"""create daily_sale table

Revision ID: 2ce3dfcb486e
Revises: 02434df3f8fa
Create Date: 2022-01-07 12:59:31.310886

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2ce3dfcb486e"
down_revision = "02434df3f8fa"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "daily_sale",
        sa.Column("id", sa.INT, primary_key=True, autoincrement=True),
        sa.Column("type", sa.TEXT, nullable=False),
        sa.Column("type_id", sa.INT, nullable=False),
        sa.Column("sale_at", sa.TIMESTAMP, nullable=False),
        sa.Column("sale_from", sa.TEXT, nullable=False),
        sa.Column("currency", sa.TEXT, nullable=True),
        sa.Column("price", sa.INT, nullable=True),
    )

    op.create_unique_constraint("uq_daily_sale", "daily_sale", ["type", "type_id", "sale_at", "sale_from"])


def downgrade():
    op.drop_table("daily_sale")
