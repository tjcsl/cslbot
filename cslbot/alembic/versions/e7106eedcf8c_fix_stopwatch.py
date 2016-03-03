# -*- coding: utf-8 -*-
"""fix stopwatch

Revision ID: e7106eedcf8c
Revises: 2ee084539c59
Create Date: 2016-03-02 21:52:28.698059

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'e7106eedcf8c'
down_revision = '2ee084539c59'
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name != 'postgresql':
        raise Exception('Currently only tested with postgres, alter and run manually if using other db')
    op.get_bind().execute('alter table stopwatches alter elapsed set data type double precision using extract(epoch from elapsed)')


def downgrade():
    if op.get_bind().dialect.name != 'postgresql':
        raise Exception('Currently only tested with postgres, alter and run manually if using other db')
    op.get_bind().execute('alter table stopwatches alter elapsed set data type timestamptz using to_timestamp(elapsed)')
