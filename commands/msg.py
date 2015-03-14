# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from helpers.command import Command
import re


@Command('msg', ['nick', 'is_admin'])
def cmd(send, msg, args):
    """Sends a message to a channel
    Syntax: !msg <channel> <message>
    """
    if not msg:
        send("Message who?")
        return
    msg = msg.split(maxsplit=1)
    if re.match("#[^ ,]{1,49}$", msg[0]):
        if len(msg) == 1:
            send("What message?")
        elif args['is_admin'](args['nick']):
            send(msg[1], target=msg[0])
        else:
            send("You are not a admin.")
    else:
        send("That is not a valid channel.")
