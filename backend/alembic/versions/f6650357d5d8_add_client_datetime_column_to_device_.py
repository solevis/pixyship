"""Add client_datetime column to device table

Revision ID: f6650357d5d8
Revises: f04491b259c1
Create Date: 2023-11-24 16:38:23.091695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6650357d5d8'
down_revision = 'f04491b259c1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('device', sa.Column('client_datetime', sa.TEXT))


def downgrade():
    op.drop_column('device', 'client_datetime')
