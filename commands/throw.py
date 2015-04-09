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
from random import choice
from helpers.command import Command


@Command('throw', ['handler', 'target'])
def cmd(send, msg, args):
    """Throw something.
    Syntax: !throw <object> at <target>
    """
    users = (list(args['handler'].channels[args['target']].users()) if args['target'] != 'private' else ['you'])
    if "into" in msg and msg != "into":
        match = re.match('(.*) into (.*)', msg)
        if match:
            msg = 'throws %s into %s' % (match.group(1), match.group(2))
            send(msg, 'action')
        else:
            return
    elif " at " in msg and msg != "at":
        match = re.match('(.*) at (.*)', msg)
        if match:
            msg = 'throws %s at %s' % (match.group(1), match.group(2))
            send(msg, 'action')
        else:
            return
    elif msg:
        msg = 'throws %s at %s' % (msg, choice(users))
        send(msg, 'action')
    else:
        send("Throw what?")
        return
