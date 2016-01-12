"""merge pending

Revision ID: 55efdbb748c
Revises: 385c29e42d9
Create Date: 2015-09-02 13:35:57.956516

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '55efdbb748c'
down_revision = '385c29e42d9'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('quotes', 'approved', new_column_name='accepted')


def downgrade():
    op.alter_column('quotes', 'accepted', new_column_name='approved')
