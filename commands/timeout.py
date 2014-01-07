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
from helpers.defer import defer


@Command('timeout', ['nick', 'is_admin', 'handler', 'target'])
def cmd(send, msg, args):
    """Quiets a user, then unquiets them after the specified period of time.
    Syntax: !timeout timespec nickname
    timespec is in the format: {number}{unit}, where unit is s, m, or h.
    """
    setmode = args['handler'].connection.mode
    if not args['is_admin'](args['nick']):
        send("Admins only")
        return
    msg = msg.split(maxsplit=1)
    time = msg[0]
    user = msg[1]
    channel = args['target']
    defer_args = [channel, " -q %s!*@*" % user]

    time_unit = time[-1].lower()
    time = int(time[:-1])
    if time_unit == "m":
        time *= 60
    if time_unit == "h":
        time *= 3600
    if time_unit == "d":
        time *= 86400

    setmode(channel, " +q %s!*@*" % user)

    defer(time, setmode, *defer_args)
