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
from ..helpers.command import Command
from ..helpers.misc import parse_time


@Command('timeout', ['nick', 'handler', 'target', 'botnick', 'config'], admin=True)
def cmd(send, msg, args):
    """Quiets a user, then unquiets them after the specified period of time.
    Syntax: {command} <timespec> <nickname>
    timespec is in the format: <number><unit>, where unit is s, m, h, or d.
    """
    nickregex = args['config']['core']['nickregex']
    setmode = args['handler'].connection.mode
    channel = args['target']
    ops = list(args['handler'].channels[channel].opers())
    if args['botnick'] not in ops:
        send("Bot must be an op.")
        return
    time, user = msg.split(maxsplit=1)
    if user == args['botnick']:
        send("I won't put myself in timeout!")
        return
    if not re.match(nickregex, user):
        send("%s is an invalid nick." % user)
        return

    time = parse_time(time)
    if time is None:
        send("Invalid unit.")
    else:
        if args['config']['feature']['networktype'] == 'unrealircd':
            setmode(channel, " +b ~q:%s!*@*" % user)
            defer_args = [channel, " -b ~q:%s!*@*" % user]
        elif args['config']['feature']['networktype'] == 'atheme':
            setmode(channel, " +q-v %s!*@* %s" % (user, user))
            defer_args = [channel, " -q %s!*@*" % user]
        else:
            raise Exception("networktype undefined or unknown in config.cfg")
        ident = args['handler'].workers.defer(time, True, setmode, *defer_args)
        send("%s has been put in timeout, ident: %d" % (user, ident))
