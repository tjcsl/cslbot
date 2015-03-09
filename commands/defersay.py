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
from helpers.misc import parse_time


@Command('defersay', ['nick', 'is_admin', 'handler'])
def cmd(send, msg, args):
    """Says something at a later time.
    Syntax: !defersay <delay> <msg>
    """
    if not args['is_admin'](args['nick']):
        send("Admins only")
        return
    msg = msg.split(maxsplit=1)
    if len(msg) != 2:
        send("Not enough arguments")
        return
    t = parse_time(msg[0])
    if t is None:
        send("Invalid unit.")
    elif t < 0:
        send("Time travel not yet implemented, sorry.")
    else:
        ident = args['handler'].workers.defer(t, False, send, msg[1])
        send("Message deferred, ident: %s" % ident)
