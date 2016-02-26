# -*- coding: utf-8 -*-
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

from sqlalchemy import func, or_

from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.orm import Log


@Command(['line', 'rline'], ['db', 'config', 'botnick'])
def cmd(send, msg, args):
    """Returns a random line from $nick.

    Syntax: {command} (--channel <channel>) (nick)

    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--channel', action=arguments.ChanParser)
    parser.add_argument('nick', nargs='*')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    quote = args['db'].query(Log.msg, Log.source)
    nick = ' '.join(cmdargs.nick) if cmdargs.nick else ""
    if nick:
        quote = quote.filter(Log.source == nick)
    else:
        quote = quote.filter(Log.source != args['botnick'])
    target = cmdargs.channels[0] if hasattr(cmdargs, 'channels') else args['config']['core']['channel']
    quote = quote.filter(
        or_(Log.type == 'pubmsg', Log.type == 'privmsg',
            Log.type == 'action'), Log.target == target, func.length(Log.msg) > 5).order_by(func.random()).first()
    if quote:
        send("%s -- %s" % quote)
    elif nick:
        send("%s isn't very quotable." % nick)
    else:
        send("Nobody is very quotable :(")
