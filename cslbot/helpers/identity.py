# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import time
from datetime import datetime, timedelta
from .orm import Nicks


def handle_nick(handler, e):
    old, new = e.source.nick, e.target
    with handler.db.session_scope() as session:
        session.add(Nicks(old=old, new=new, time=time.time()))
        if handler.config['feature'].getboolean('nickkick'):
            return do_kick(handler, session, new)
        else:
            return False


def get_chain(session, nick, limit=0):
    # Search backwards, getting previous nicks for a (optionally) limited amount of time.
    chain = []
    curr_time = time.time()
    curr = nick
    while curr is not None:
        chain.append(curr)
        row = session.query(Nicks).filter(Nicks.new == curr, ~Nicks.old.startswith('Guest'), Nicks.time < curr_time, Nicks.time >= limit).order_by(Nicks.time).limit(1).first()
        if row is not None:
            curr = row.old
            curr_time = row.time
        else:
            curr = None
    return list(reversed(chain))


def do_kick(handler, session, nick):
    # only go 5 minutes back for identity crisis detection.
    limit = datetime.now() - timedelta(minutes=5)
    chain = get_chain(session, nick, limit.timestamp())
    # more than 2 nick changes in 5 minutes.
    return True if len(chain) > 3 else False
