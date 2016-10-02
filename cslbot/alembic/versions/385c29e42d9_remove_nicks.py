# -*- coding: utf-8 -*-
"""remove nicks.

Revision ID: 385c29e42d9
Revises: 3614b38ddf9
Create Date: 2015-05-02 13:52:39.759794

"""

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '385c29e42d9'
down_revision = '3614b38ddf9'
branch_labels = None
depends_on = None


def upgrade():
    # FIXME: make sure this works everywhere.
    op.get_bind().execute('DROP TABLE IF EXISTS nicks')
    # op.drop_table('nicks')


def downgrade():
    op.create_table(
        'nicks',
        sa.Column(
            'old', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            'new', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            'time', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            'id', sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint(
            'id', name='nicks_pkey'))
