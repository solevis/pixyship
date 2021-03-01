"""track reference changes

Revision ID: e98016f3cfec
Revises: a2ac148441cf
Create Date: 2018-09-24 21:49:20.811276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.dialects.postgresql import UUID

revision = 'e98016f3cfec'
down_revision = 'a2ac148441cf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'record',
        sa.Column('id', sa.INT, primary_key=True),
        sa.Column('type', sa.TEXT, nullable=False),
        sa.Column('type_id', sa.INT, nullable=False),
        sa.Column('current', sa.BOOLEAN, nullable=False),
        sa.Column('md5_hash', UUID, nullable=False),
        sa.Column('data', sa.TEXT, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    )
    op.create_index('idx_record__type_type_id_primary', 'record', ['type', 'type_id', 'current'])


def downgrade():
    op.drop_table('record')
