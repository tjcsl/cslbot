# -*- coding: utf-8 -*-
# Copyright (C) 2013-2017 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from ..helpers.command import Command
from ..helpers.orm import Log


def get_last(cursor, cmdchar, ctrlchan, nick):
    command = '%sseen %s' % (cmdchar, nick)
    return cursor.query(Log).filter(Log.source.ilike(nick), Log.target != ctrlchan, Log.msg != command,
                                    Log.type != 'join').order_by(Log.time.desc()).first()


@Command('seen', ['db', 'config'])
def cmd(send, msg, args):
    """When a nick was last seen.

    Syntax: {command} <nick>

    """
    if not msg:
        send("Seen who?")
        return
    cmdchar, ctrlchan = args['config']['core']['cmdchar'], args['config']['core']['ctrlchan']
    last = get_last(args['db'], cmdchar, ctrlchan, msg)
    if last is None:
        send("%s has never shown their face." % msg)
        return
    delta = datetime.now() - last.time
    # We only need second-level precision.
    delta -= delta % timedelta(seconds=1)
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
    elif last.type == 'topic':
        output += 'changing topic to %s' % last.msg
    elif last.type in ['pubnotice', 'privnotice']:
        output += 'sending notice %s' % last.msg
    elif last.type == 'mode':
        output += 'setting mode %s' % last.msg
    else:
        raise Exception("Invalid type.")
    send(output)
