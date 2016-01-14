"""use datetime, not float

Revision ID: 243c9cf0eb7d
Revises: 4d165186b4ed
Create Date: 2016-01-14 14:45:09.107882

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '243c9cf0eb7d'
down_revision = '4d165186b4ed'
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name != 'postgresql':
        raise Exception('Currently only tested with postgres, alter and run manually if using other db')
    op.get_bind().execute('alter table urls alter time set data type timestamptz using to_timestamp(time)')
    op.get_bind().execute('alter table notes alter time set data type timestamptz using to_timestamp(time)')
    op.get_bind().execute('alter table log alter time set data type timestamptz using to_timestamp(time)')
    op.get_bind().execute('alter table stopwatches alter time set data type timestamptz using to_timestamp(time)')
    op.get_bind().execute('alter table stopwatches alter elapsed set data type timestamptz using to_timestamp(elapsed)')
    op.get_bind().execute('alter table ignore alter expire set data type timestamptz using to_timestamp(expire)')


def downgrade():
    if op.get_bind().dialect.name != 'postgresql':
        raise Exception('Currently only tested with postgres, alter and run manually if using other db')
    op.get_bind().execute('alter table urls alter time set data type double precision using extract(epoch from time)')
    op.get_bind().execute('alter table notes alter time set data type double precision using extract(epoch from time)')
    op.get_bind().execute('alter table log alter time set data type double precision using extract(epoch from time)')
    op.get_bind().execute('alter table stopwatches alter time set data type double precision using extract(epoch from time)')
    op.get_bind().execute('alter table stopwatches alter elapsed set data type double precision using extract(epoch from elapsed)')
    op.get_bind().execute('alter table ignore alter expire set data type double precision using extract(epoch from expire)')
