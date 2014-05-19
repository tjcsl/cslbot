
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

from helpers.command import Command
from helpers.textutils import gen_clippy


@Command('clippy', ['nick'])
def cmd(send, msg, args):
    """Informs a user that they are trying to do something and inquire if they want help
    Syntax: {command} <nick> <action>
    """
    msg = msg.split()
    if not msg:
        send(gen_clippy(args['nick'], "IRC"))
    elif len(msg) == 1:
        send(gen_clippy(args['nick'], msg[0]))
    else:
        send(gen_clippy(msg[0], " ".join(msg[1:])))
