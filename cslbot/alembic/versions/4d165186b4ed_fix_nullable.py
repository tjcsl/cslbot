"""fix nullable.

Revision ID: 4d165186b4ed
Revises: 7fde00129eb6
Create Date: 2016-01-14 14:44:45.878579

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4d165186b4ed'
down_revision = '7fde00129eb6'
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name == 'sqlite':
        with op.batch_alter_table('babble') as batch_op:
            batch_op.alter_column('key', existing_type=sa.VARCHAR(length=512), nullable=True)
            batch_op.alter_column('source', existing_type=sa.TEXT(), nullable=True)
            batch_op.alter_column('target', existing_type=sa.TEXT(), nullable=True)
            batch_op.alter_column('word', existing_type=sa.TEXT(), nullable=True)
    else:
        op.alter_column('babble', 'key', existing_type=sa.VARCHAR(length=512), nullable=True)
        op.alter_column('babble', 'source', existing_type=sa.TEXT(), nullable=True)
        op.alter_column('babble', 'target', existing_type=sa.TEXT(), nullable=True)
        op.alter_column('babble', 'word', existing_type=sa.TEXT(), nullable=True)


def downgrade():
    if op.get_bind().dialect.name == 'sqlite':
        with op.batch_alter_table('babble') as batch_op:
            batch_op.alter_column('word', existing_type=sa.TEXT(), nullable=False)
            batch_op.alter_column('target', existing_type=sa.TEXT(), nullable=False)
            batch_op.alter_column('source', existing_type=sa.TEXT(), nullable=False)
            batch_op.alter_column('key', existing_type=sa.VARCHAR(length=512), nullable=False)
    else:
        op.alter_column('babble', 'word', existing_type=sa.TEXT(), nullable=False)
        op.alter_column('babble', 'target', existing_type=sa.TEXT(), nullable=False)
        op.alter_column('babble', 'source', existing_type=sa.TEXT(), nullable=False)
        op.alter_column('babble', 'key', existing_type=sa.VARCHAR(length=512), nullable=False)
