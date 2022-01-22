"""Add modifications to listing

Revision ID: a2ac148441cf
Revises: ea831971898f
Create Date: 2018-06-17 12:54:38.744709

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a2ac148441cf'
down_revision = 'ea831971898f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('listing', sa.Column('modification', sa.TEXT))


def downgrade():
    op.drop_column('listing', 'modification')
