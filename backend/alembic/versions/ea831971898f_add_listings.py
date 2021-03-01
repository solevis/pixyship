"""Add listings

Revision ID: ea831971898f
Revises: bdc90a07b024
Create Date: 2018-06-17 09:27:19.695346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea831971898f'
down_revision = 'bdc90a07b024'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'listing',
        sa.Column('id', sa.INT, primary_key=True),
        sa.Column('sale_at', sa.TIMESTAMP, nullable=False),
        sa.Column('item_name', sa.TEXT, nullable=False),
        sa.Column('item_id', sa.INT, nullable=False),
        sa.Column('amount', sa.INT, nullable=False),
        sa.Column('currency', sa.TEXT, nullable=False),
        sa.Column('price', sa.INT, nullable=False),
        sa.Column('user_id', sa.INT, nullable=False),
    )


def downgrade():
    op.drop_table('listing')
