"""fix nullable

Revision ID: 4d165186b4ed
Revises: 7fde00129eb6
Create Date: 2016-01-14 14:44:45.878579

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d165186b4ed'
down_revision = '7fde00129eb6'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('babble', 'key',
                    existing_type=sa.VARCHAR(length=512),
                    nullable=True)
    op.alter_column('babble', 'source',
                    existing_type=sa.TEXT(),
                    nullable=True)
    op.alter_column('babble', 'target',
                    existing_type=sa.TEXT(),
                    nullable=True)
    op.alter_column('babble', 'word',
                    existing_type=sa.TEXT(),
                    nullable=True)


def downgrade():
    op.alter_column('babble', 'word',
                    existing_type=sa.TEXT(),
                    nullable=False)
    op.alter_column('babble', 'target',
                    existing_type=sa.TEXT(),
                    nullable=False)
    op.alter_column('babble', 'source',
                    existing_type=sa.TEXT(),
                    nullable=False)
    op.alter_column('babble', 'key',
                    existing_type=sa.VARCHAR(length=512),
                    nullable=False)
