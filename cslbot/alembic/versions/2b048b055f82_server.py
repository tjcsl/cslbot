"""server

Revision ID: 2b048b055f82
Revises: e7106eedcf8c
Create Date: 2021-05-23 14:00:25.372117

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2b048b055f82'
down_revision = 'e7106eedcf8c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('server', sa.UnicodeText(), nullable=True))


def downgrade():
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.drop_column('server')
