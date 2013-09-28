
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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


@Command('clippy')
def cmd(send, msg, args):
    """Informs a user that they are trying to do something and inquire if they want help
    Syntax: !clippy <nick> <action>
    """
    msg = msg.split()
    if len(msg) < 1:
        send("Syntax: !clippy <nick> <action>")
        return
    if len(msg) < 2:
        send('Clippy can\'t determine what %s is trying to do!' % msg[0])
        return
    send('%s: I see you are trying to %s, would you like some help with that?' % (msg[0], " " .join(msg[1:])))
