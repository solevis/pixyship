"""Initial

Revision ID: cf08232a3b60
Revises:
Create Date: 2018-05-25 23:24:14.830218

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.

revision = 'cf08232a3b60'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'player',
        sa.Column('id', sa.INT, primary_key=True),
        sa.Column('name', sa.TEXT, nullable=False),
        sa.Column('trophies', sa.INT, nullable=False),
        sa.Column('alliance_id', sa.INT),
        sa.Column('last_login_at', sa.TIMESTAMP)
    )


def downgrade():
    op.drop_table('player')
