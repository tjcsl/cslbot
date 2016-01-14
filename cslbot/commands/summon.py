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

from datetime import datetime

from ..helpers.command import Command
from ..helpers.orm import Notes


@Command('summon', ['db', 'nick', 'type'], limit=5)
def cmd(send, msg, args):
    """Summons a user
    Syntax: {command} <nick>
    """
    if args['type'] == 'privmsg':
        send("Note-passing should be done in public.")
        return
    arguments = msg.split()
    if len(arguments) > 1:
        send("Sorry, I can only perform the summoning ritual for one person at a time")
        return
    elif len(arguments) == 0:
        send("Who shall I summon?")
        return
    nick = arguments[0]
    message = "You have been summoned!"
    row = Notes(note=message, submitter="The Dark Gods", nick=nick, time=datetime.now())
    args['db'].add(row)
    send("%s has been summoned!" % nick)
