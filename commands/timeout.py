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


@Command('timeout', ['nick', 'is_admin', 'handler', 'target', 'botnick'])
def cmd(send, msg, args):
    """Quiets a user, then unquiets them after the specified period of time.
    Syntax: !timeout timespec nickname
    timespec is in the format: {number}{unit}, where unit is s, m, h, or d.
    """
    setmode = args['handler'].connection.mode
    channel = args['target']
    ops = list(args['handler'].channels[channel].opers())
    if not args['is_admin'](args['nick']):
        send("Ops only")
        return
    if args['botnick'] not in ops:
        send("Bot must be an op.")
        return
    time, user = msg.split(maxsplit=1)
    defer_args = [channel, " -q %s!*@*" % user]

    time = parse_time(time)
    if time is None:
        send("Invalid unit.")
    else:
        setmode(channel, " +q %s!*@*" % user)
        ident = args['handler'].workers.defer(time, setmode, *defer_args)
        send("%s has been put in timeout, ident: %d" % (user, ident))
