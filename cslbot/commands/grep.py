# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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
from ..helpers.misc import escape


@Command(['grep', 'loggrep'], ['config', 'db'], limit=5)
def cmd(send, msg, args):
    """Greps the log for a string.

    Syntax: {command} [--nick <nick>] [--ignore-case/-i] <string>

    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--nick', action=arguments.NickParser)
    parser.add_argument('--ignore-case', '-i', action='store_true')
    parser.add_argument('string', nargs='*')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if not cmdargs.string:
        send('Please specify a search term.')
        return
    cmdchar = args['config']['core']['cmdchar']
    term = ' '.join(cmdargs.string)
    if cmdargs.nick:
        query = args['db'].query(Log).filter(Log.type == 'pubmsg', Log.source == cmdargs.nick, ~Log.msg.startswith(cmdchar))
    else:
        query = args['db'].query(Log).filter(Log.type == 'pubmsg', ~Log.msg.startswith(cmdchar))
    if cmdargs.ignore_case:
        query = query.filter(Log.msg.ilike('%%%s%%' % escape(term)))
    else:
        query = query.filter(Log.msg.like('%%%s%%' % escape(term)))
    query = query.order_by(Log.time.desc())
    result = query.limit(1).first()
    count = query.count()
    if result is not None:
        logtime = result.time.strftime('%Y-%m-%d %H:%M:%S')
        send("%s was last said by %s at %s (%d occurrences)" % (result.msg, result.source, logtime, count))
    elif cmdargs.nick:
        send('%s has never said %s.' % (cmdargs.nick, term))
    else:
        send('%s has never been said.' % term)
