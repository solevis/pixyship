"""Add market_message table

Revision ID: f04491b259c1
Revises: 1b988e6cf456
Create Date: 2022-07-09 19:25:16.425768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f04491b259c1'
down_revision = '1b988e6cf456'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'market_message',
        sa.Column('id', sa.INT, primary_key=True),
        sa.Column('message', sa.TEXT, nullable=False),
        sa.Column('sale_id', sa.INT, nullable=False),
        sa.Column('item_id', sa.INT, nullable=False),
        sa.Column('user_id', sa.INT, nullable=False),
        sa.Column('message_type', sa.TEXT, nullable=False),
        sa.Column('channel_id', sa.TEXT, nullable=False),
        sa.Column('activit_type', sa.TEXT, nullable=False),
        sa.Column('message_date', sa.TIMESTAMP, nullable=False),
    )

    op.create_unique_constraint('uq_market_message', 'market_message', ['sale_id'])


def downgrade():
    op.drop_table('market_message')
