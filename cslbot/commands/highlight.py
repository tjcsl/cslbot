# -*- coding: utf-8 -*-
# Copyright (C) 2013-2017 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.orm import Log


@Command('highlight', ['db', 'nick', 'config', 'target', 'botnick'])
def cmd(send, msg, args):
    """When a nick was last pinged.

    Syntax: {command} [--channel #channel] [nick]

    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--channel', nargs='?', action=arguments.ChanParser)
    parser.add_argument('nick', nargs='?', action=arguments.NickParser, default=args['nick'])
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if args['target'] == 'private':
        send("You're always the highlight of your monologues!")
        return
    target = cmdargs.channels[0] if hasattr(cmdargs, 'channels') else args['target']
    row = args['db'].query(Log).filter(
        Log.msg.ilike("%%%s%%" % cmdargs.nick), ~Log.msg.contains('%shighlight' % args['config']['core']['cmdchar']), Log.target == target,
        Log.source != args['botnick'], Log.source != cmdargs.nick,
        (Log.type == 'pubmsg') | (Log.type == 'privmsg') | (Log.type == 'action')).order_by(Log.time.desc()).first()
    if row is None:
        send("%s has never been pinged." % cmdargs.nick)
    else:
        time = row.time.strftime('%Y-%m-%d %H:%M:%S')
        send("%s <%s> %s" % (time, row.source, row.msg))
