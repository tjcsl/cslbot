# -*- coding: utf-8 -*-
"""merge pending.

Revision ID: 55efdbb748c
Revises: 385c29e42d9
Create Date: 2015-09-02 13:35:57.956516

"""

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "55efdbb748c"
down_revision = "385c29e42d9"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("quotes") as batch_op:
            batch_op.add_column(sa.Column("accepted", sa.Integer(), nullable=True))
            batch_op.drop_column("approved")
    else:
        op.alter_column("quotes", "approved", new_column_name="accepted")


def downgrade():
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("quotes") as batch_op:
            batch_op.add_column(sa.Column("approved", sa.Integer(), nullable=True))
            batch_op.drop_column("accepted")
    else:
        op.alter_column("quotes", "accepted", new_column_name="approved")
