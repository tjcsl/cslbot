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

import re
from time import time
from helpers.orm import Notes
from helpers.command import Command


@Command('note', ['db', 'nick', 'type', 'config'], limit=5)
def cmd(send, msg, args):
    """Leaves a note for a user or users.
    Syntax: !note <nick(,nick2)> <note>
    """
    if not args['config']['feature'].getboolean('hooks'):
        send("Hooks are disabled, and this command depends on hooks. Please contact the bot admin(s).")
        return
    if args['type'] == 'privmsg':
        send("Note-passing should be done in public.")
        return
    try:
        nick, note = msg.split(maxsplit=1)
        nicks = set(x for x in nick.split(',') if x)
    except ValueError:
        send("Not enough arguments.")
        return
    nickregex = args['config']['core']['nickregex'] + '+$'
    for nick in nicks:
        if re.match(nickregex, nick):
            row = Notes(note=note, submitter=args['nick'], nick=nick, time=time())
            args['db'].add(row)
            send("Note left for %s." % nick)
        else:
            send("Invalid nick: %s" % nick)
