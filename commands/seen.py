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

import time
from datetime import timedelta
from helpers.orm import Log
from helpers.command import Command


def get_last(cursor, nick):
    return cursor.query(Log).filter(Log.source.ilike(nick), Log.type != 'join').order_by(Log.time.desc()).first()


@Command('seen', ['db'])
def cmd(send, msg, args):
    """When a nick was last seen.
    Syntax: !seen <nick>
    """
    if not msg:
        send("Seen who?")
        return
    last = get_last(args['db'], msg)
    if last is None:
        send("%s has never shown his face." % msg)
        return
    elapsed = time.time() - last.time
    delta = timedelta(seconds=int(elapsed))
    output = "%s was last seen %s ago " % (msg, delta)
    if last.type == 'pubmsg' or last.type == 'privmsg':
        output += 'saying "%s"' % last.msg
    elif last.type == 'action':
        output += 'doing "%s"' % last.msg
    elif last.type == 'part':
        output += 'leaving and saying "%s"' % last.msg
    elif last.type == 'nick':
        output += 'nicking to %s' % last.msg
    elif last.type == 'quit':
        output += 'quiting and saying "%s"' % last.msg
    elif last.type == 'kick':
        output += 'kicking %s for "%s"' % last.msg.split(',')
    else:
        raise Exception("Invalid type.")
    send(output)
