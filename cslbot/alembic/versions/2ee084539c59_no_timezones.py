# -*- coding: utf-8 -*-
"""no timezones.

Revision ID: 2ee084539c59
Revises: 243c9cf0eb7d
Create Date: 2016-01-15 11:04:59.297085

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2ee084539c59"
down_revision = "243c9cf0eb7d"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name != "postgresql":
        raise Exception(
            "Currently only tested with postgres, alter and run manually if using other db"
        )
    op.get_bind().execute("alter table urls alter time set data type timestamp")
    op.get_bind().execute("alter table notes alter time set data type timestamp")
    op.get_bind().execute("alter table log alter time set data type timestamp")
    op.get_bind().execute("alter table stopwatches alter time set data type timestamp")
    op.get_bind().execute("alter table stopwatches alter elapsed set data type timestamp")
    op.get_bind().execute("alter table ignore alter expire set data type timestamp")


def downgrade():
    if op.get_bind().dialect.name != "postgresql":
        raise Exception(
            "Currently only tested with postgres, alter and run manually if using other db"
        )
    op.get_bind().execute("alter table urls alter time set data type timestamptz")
    op.get_bind().execute("alter table notes alter time set data type timestamptz")
    op.get_bind().execute("alter table log alter time set data type timestamptz")
    op.get_bind().execute("alter table stopwatches alter time set data type timestamptz")
    op.get_bind().execute("alter table stopwatches alter elapsed set data type timestamptz")
    op.get_bind().execute("alter table ignore alter expire set data type timestamptz")
