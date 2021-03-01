"""Remove modification column in listing

Revision ID: 6033f73dc5ea
Revises: 7da533ce19c6
Create Date: 2021-02-28 19:08:29.699911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6033f73dc5ea'
down_revision = '7da533ce19c6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('listing', 'modification')


def downgrade():
    op.add_column('listing', sa.Column('modification', sa.TEXT))
