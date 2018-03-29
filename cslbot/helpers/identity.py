# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from datetime import datetime, timedelta

from .orm import Log


def handle_nick(handler, e):
    with handler.db.session_scope() as session:
        if handler.config['feature'].getboolean('nickkick'):
            return do_kick(session, e.target)
        else:
            return False


def get_chain(session, nick, limit=datetime.min):
    # Search backwards, getting previous nicks for a (optionally) limited amount of time.
    chain = []
    curr_time = datetime.now()
    curr = nick
    while curr is not None:
        row = session.query(Log).filter(Log.msg == curr, Log.type == 'nick', ~Log.source.startswith('Guest'), Log.time < curr_time,
                                        Log.time >= limit).order_by(Log.time.desc()).limit(1).first()
        if row is not None:
            curr = row.source
            chain.append(curr)
            curr_time = row.time
        else:
            curr = None
    if chain:
        chain.insert(0, nick)
    return list(reversed(chain))


def do_kick(session, nick):
    # only go 5 minutes back for identity crisis detection.
    limit = datetime.now() - timedelta(minutes=5)
    chain = get_chain(session, nick, limit)
    # more than 2 nick changes in 5 minutes.
    return True if len(chain) > 3 else False
