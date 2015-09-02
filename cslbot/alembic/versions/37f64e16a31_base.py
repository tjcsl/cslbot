"""base

Revision ID: 37f64e16a31
Revises:
Create Date: 2015-09-02 17:00:27.486025

"""

# revision identifiers, used by Alembic.
revision = '37f64e16a31'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('babble',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('key', sa.Unicode(length=512), nullable=True),
                    sa.Column('source', sa.UnicodeText(), nullable=True),
                    sa.Column('target', sa.UnicodeText(), nullable=True),
                    sa.Column('word', sa.UnicodeText(), nullable=True),
                    sa.Column('freq', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    mysql_row_format='dynamic'
                    )
    op.create_index(op.f('ix_babble_key'), 'babble', ['key'], unique=False)
    op.create_table('babble_count',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.UnicodeText(), nullable=True),
                    sa.Column('key', sa.UnicodeText(), nullable=True),
                    sa.Column('count', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('babble_last',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('last', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('commands',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('nick', sa.UnicodeText(), nullable=True),
                    sa.Column('command', sa.UnicodeText(), nullable=True),
                    sa.Column('channel', sa.UnicodeText(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('ignore',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('nick', sa.UnicodeText(), nullable=True),
                    sa.Column('expire', sa.Float(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('issues',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.UnicodeText(), nullable=True),
                    sa.Column('source', sa.UnicodeText(), nullable=True),
                    sa.Column('description', sa.UnicodeText(), nullable=True),
                    sa.Column('accepted', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('log',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('source', sa.UnicodeText(), nullable=True),
                    sa.Column('target', sa.Unicode(length=512), nullable=True),
                    sa.Column('flags', sa.Integer(), nullable=True),
                    sa.Column('msg', sa.UnicodeText(), nullable=True),
                    sa.Column('type', sa.UnicodeText(), nullable=True),
                    sa.Column('time', sa.Float(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_log_target'), 'log', ['target'], unique=False)
    op.create_table('notes',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('note', sa.UnicodeText(), nullable=True),
                    sa.Column('submitter', sa.UnicodeText(), nullable=True),
                    sa.Column('nick', sa.UnicodeText(), nullable=True),
                    sa.Column('time', sa.Float(), nullable=True),
                    sa.Column('pending', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('polls',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('question', sa.UnicodeText(), nullable=True),
                    sa.Column('active', sa.Integer(), nullable=True),
                    sa.Column('deleted', sa.Integer(), nullable=True),
                    sa.Column('accepted', sa.Integer(), nullable=True),
                    sa.Column('submitter', sa.UnicodeText(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('quotes',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('quote', sa.UnicodeText(), nullable=True),
                    sa.Column('nick', sa.UnicodeText(), nullable=True),
                    sa.Column('submitter', sa.UnicodeText(), nullable=True),
                    sa.Column('approved', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('scores',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('nick', sa.Unicode(length=20), nullable=True),
                    sa.Column('score', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('nick')
                    )
    op.create_table('stopwatches',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('active', sa.Integer(), nullable=True),
                    sa.Column('time', sa.Integer(), nullable=True),
                    sa.Column('elapsed', sa.Float(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('tumblrs',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('post', sa.UnicodeText(), nullable=True),
                    sa.Column('blogname', sa.UnicodeText(), nullable=True),
                    sa.Column('submitter', sa.UnicodeText(), nullable=True),
                    sa.Column('accepted', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('urls',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('url', sa.UnicodeText(), nullable=True),
                    sa.Column('title', sa.UnicodeText(), nullable=True),
                    sa.Column('nick', sa.UnicodeText(), nullable=True),
                    sa.Column('time', sa.Float(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('weather_prefs',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('nick', sa.Unicode(length=20), nullable=True),
                    sa.Column('location', sa.UnicodeText(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('nick')
                    )
    op.create_table('poll_responses',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('response', sa.UnicodeText(), nullable=True),
                    sa.Column('voter', sa.UnicodeText(), nullable=True),
                    sa.Column('pid', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['pid'], ['polls.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('poll_responses')
    op.drop_table('weather_prefs')
    op.drop_table('urls')
    op.drop_table('tumblrs')
    op.drop_table('stopwatches')
    op.drop_table('scores')
    op.drop_table('quotes')
    op.drop_table('polls')
    op.drop_table('notes')
    op.drop_index(op.f('ix_log_target'), table_name='log')
    op.drop_table('log')
    op.drop_table('issues')
    op.drop_table('ignore')
    op.drop_table('commands')
    op.drop_table('babble_last')
    op.drop_table('babble_count')
    op.drop_index(op.f('ix_babble_key'), table_name='babble')
    op.drop_table('babble')
