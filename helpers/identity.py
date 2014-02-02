# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from time import time
from datetime import datetime, timedelta
from operator import itemgetter


def handle_nick(handler, e):
    old, new = e.source.nick, e.target
    cursor = handler.db.get()
    cursor.execute('INSERT INTO nicks VALUES(%s,%s,%s)', (old, new, time()))
    if handler.config['feature'].getboolean('nickkick'):
        return do_kick(handler, cursor, new)
    else:
        return False


def get_mapping(cursor, nick, limit):
    mapping = {}
    done = set()
    todo = set([nick])
    while todo:
        curr = todo.pop()
        prev = cursor.execute('SELECT old,time FROM nicks WHERE new=%s AND time>=%s ORDER BY time', (curr, limit)).fetchall()
        done.add(curr)
        for x in prev:
            if x['old'] not in done:
                todo.add(x['old'])
        mapping[curr] = [dict(x) for x in prev]
    return mapping


def get_chain(cursor, nick, limit=0):
    # Search backwards, getting previous nicks for a (optionally) limited amount of time.
    mapping = get_mapping(cursor, nick, limit)
    chain = [nick]
    curr = mapping[nick]
    while curr:
        last = sorted(curr, key=itemgetter('time'))
        if last:
            last = last[0]['old']
            curr = None if last in chain else mapping[last]
            chain.append(last)
    return list(reversed(chain))


def do_kick(handler, cursor, nick):
    # only go 5 minutes back for identity crisis detection.
    limit = datetime.now() - timedelta(minutes=5)
    chain = get_chain(cursor, nick, limit.timestamp())
    # more than 2 nick changes in 5 minutes.
    return True if len(chain) > 3 else False
