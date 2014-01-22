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
from collections import OrderedDict


def handle_nick(handler, e):
    curr, new = e.source.nick, e.target
    cursor = handler.db.get()
    cursor.execute('INSERT INTO nicks VALUES(?,?,?)', (curr, new, time()))
    cursor.commit()
    if bool(handler.config['feature']['nickkick']):
        do_kick(handler, cursor, new)


def get_chain(cursor, nick, limit=None):
    # Search backwards, getting previous nicks for a (optionally) limited amount of time.
    chain = OrderedDict()
    while nick is not None:
        prev = cursor.execute('SELECT curr, time FROM nicks WHERE new=? AND time >= ? ORDER BY time ASC LIMIT 1', (nick, limit)).fetchall()
        if prev:
            nick = prev['curr']
            chain[nick] = prev['time']
        else:
            nick = None
    return chain


def do_kick(handler, cursor, nick):
    # only go 5 minutes back.
    limit = datetime.now() - timedelta(minutes=5)
    chain = get_chain(cursor, nick, limit.timestamp())
    print(chain)
    if len(chain) > 1:
    #FIXME: handler.do_kick()
        print("kicking")
