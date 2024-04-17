"""Add trigram index to player

Revision ID: 7da533ce19c6
Revises: 72992fac062b
Create Date: 2019-09-14 18:08:02.844596

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "7da533ce19c6"
down_revision = "72992fac062b"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE INDEX idx_tgrm_player_name ON player USING GIN(name gin_trgm_ops)")
    op.execute("CREATE INDEX idx_player_trophies ON player (trophies)")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP INDEX IF EXISTS idx_tgrm_player_name")
    op.execute("DROP INDEX IF EXISTS idx_player_trophies")
