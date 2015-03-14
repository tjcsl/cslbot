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


@Command('cancel', ['nick', 'is_admin', 'handler'])
def cmd(send, msg, args):
    """Cancels a deferred action with the given id.
    Syntax: !cancel id
    """
    if not args['is_admin'](args['nick']):
        send("Only admins can cancel threads.")
        return
    try:
        args['handler'].workers.cancel(int(msg))
    except ValueError:
        send("Index must be a digit.")
        return
    except KeyError:
        send("No such event.")
        return
    send("Event canceled.")
