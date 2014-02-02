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

import re
from helpers.command import Command


def get_log(conn, user, target):
    if user is None:
        cursor = conn.execute("SELECT msg FROM log WHERE (target=%s AND type='pubmsg') ORDER BY time DESC", (target,))
        # Don't parrot back the !reverse call.
        cursor.fetchone()
    else:
        cursor = conn.execute("SELECT msg FROM log WHERE (source=%s AND target=%s AND type='pubmsg') ORDER BY time DESC", (user, target))
    return cursor.fetchone()


@Command(['reverse', 'sdamashek'], ['db', 'target'])
def cmd(send, msg, args):
    """Reverses a message.
    Syntax: !reverse --<nick>
    """
    conn = args['db'].get()
    user = msg[2:] if re.search("^--", msg) else None
    if msg and not user:
        send(msg[::-1].strip())
        return
    log = get_log(conn, user, args['target'])
    if user and not log:
        send("Couldn't find a message from %s :(" % user)
    else:
        send(log['msg'][::-1])
