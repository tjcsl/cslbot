# -*- coding: utf-8 -*-
"""kick logging change

Revision ID: 3614b38ddf9
Revises: ef7ccebeff
Create Date: 2015-04-23 15:55:07.747669

"""

from alembic import op

import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3614b38ddf9'
down_revision = 'ef7ccebeff'
branch_labels = None
depends_on = None


def upgrade():
    log = sa.table('log', sa.column('type', sa.String), sa.column('msg', sa.String))
    rows = op.get_bind().execute(log.select().where(log.c.type == 'kick').where(log.c.msg.like('%,%'))).fetchall()
    rows = [x for x in rows if ',' in x.msg and x.msg.find(',') < x.msg.find(' ')]
    if not rows:
        return
    values = [{'old_msg': x.msg, 'msg': x.msg.replace(',', ' ', 1)} for x in rows]
    op.get_bind().execute(log.update().where(log.c.msg == sa.bindparam('old_msg')).values(msg=sa.bindparam('msg')), values)


def downgrade():
    # FIXME: this adds extraneous commas
    return
    log = sa.table('log', sa.column('type', sa.String), sa.column('msg', sa.String))
    rows = op.get_bind().execute(log.select().where(log.c.type == 'kick')).fetchall()
    rows = [x for x in rows if ',' not in x.msg or x.msg.find(' ') < x.msg.find(',')]
    if not rows:
        return
    values = [{'old_msg': x.msg, 'msg': x.msg.replace(' ', ',', 1)} for x in rows]
    op.get_bind().execute(log.update().where(log.c.msg == sa.bindparam('old_msg')).values(msg=sa.bindparam('msg')), values)
