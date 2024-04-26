"""Change record.type column from text to Enum

Revision ID: 6f6fcebc52f2
Revises: ad2529eaf52f
Create Date: 2024-04-23 23:36:12.240436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f6fcebc52f2'
down_revision = '7b4cf67136ba'
branch_labels = None
depends_on = None


def upgrade():
    type_enum = sa.Enum(
        'achievement',
        'character',
        'collection',
        'craft',
        'item',
        'missile',
        'prestige',
        'research',
        'room',
        'room_sprite',
        'ship',
        'skin',
        'skinset',
        'sprite',
        'training',
        name='type_enum'
    )
    type_enum.create(op.get_bind(), checkfirst=False)

    op.alter_column('record', 'type',
                    existing_type=sa.Text(),
                    type_=type_enum,
                    existing_nullable=True,
                    postgresql_using='type::text::type_enum')


def downgrade():
    op.alter_column('record', 'type',
                    existing_type=sa.Enum(name='type_enum'),
                    type_=sa.Text(),
                    existing_nullable=True,
                    postgresql_using='type::text')

    sa.Enum(name="type_enum").drop(op.get_bind(), checkfirst=False)
