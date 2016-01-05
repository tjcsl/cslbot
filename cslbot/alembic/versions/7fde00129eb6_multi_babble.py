"""multi-babble

Revision ID: 7fde00129eb6
Revises: 55efdbb748c
Create Date: 2016-01-05 13:55:38.649710

"""

# revision identifiers, used by Alembic.
revision = '7fde00129eb6'
down_revision = '55efdbb748c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('babble2',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('key', sa.Unicode(length=512), nullable=True),
                    sa.Column('source', sa.UnicodeText(), nullable=True),
                    sa.Column('target', sa.UnicodeText(), nullable=True),
                    sa.Column('word', sa.UnicodeText(), nullable=True),
                    sa.Column('freq', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_row_format='dynamic'
                    )
    op.create_index(op.f('ix_babble2_key'), 'babble2', ['key'], unique=False)
    op.add_column('babble_count', sa.Column(
        'length', sa.Integer(), nullable=True))
    op.add_column('babble_last', sa.Column(
        'length', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('babble_last', 'length')
    op.drop_column('babble_count', 'length')
    op.drop_index(op.f('ix_babble2_key'), table_name='babble2')
    op.drop_table('babble2')
