# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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
from datetime import datetime

from ..helpers.command import Command
from ..helpers.orm import Notes


@Command('note', ['db', 'nick', 'type', 'config'], limit=5)
def cmd(send, msg, args):
    """Leaves a note for a user or users.

    Syntax: {command} <nick>[,nick2,...] <note>

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
    successful_nicks = []
    failed_nicks = []
    for nick in nicks:
        if re.match(nickregex, nick):
            row = Notes(note=note, submitter=args['nick'], nick=nick, time=datetime.now())
            args['db'].add(row)
            successful_nicks.append(nick)
        else:
            failed_nicks.append(nick)
    if successful_nicks:
        send("Note left for %s." % ", ".join(successful_nicks))
    if failed_nicks:
        send("Invalid nick(s): %s." % ", ".join(failed_nicks))
