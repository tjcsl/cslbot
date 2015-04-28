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

from time import strftime, localtime
from ..helpers.orm import Log
from ..helpers import arguments
from ..helpers.command import Command


@Command(['grep', 'loggrep'], ['config', 'db'])
def cmd(send, msg, args):
    """Greps the log for a string.
    Syntax: {command} [--nick <nick>] <string>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--nick', action=arguments.NickParser)
    parser.add_argument('string', nargs='?')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if not cmdargs.string:
        send('Please specify a search term.')
        return
    cmdchar = args['config']['core']['cmdchar']
    if cmdargs.nick:
        row = args['db'].query(Log).filter(Log.type == 'pubmsg', Log.source == cmdargs.nick, ~Log.msg.startswith(cmdchar),
                                           Log.msg.like('%' + cmdargs.string + '%')).order_by(Log.id.desc()).first()
    else:
        row = args['db'].query(Log).filter(Log.type == 'pubmsg', ~Log.msg.startswith(cmdchar), Log.msg.like('%' + cmdargs.string + '%')).order_by(Log.id.desc()).first()
    if row:
        logtime = strftime('%Y-%m-%d %H:%M:%S', localtime(row.time))
        send("%s said %s at %s" % (row.source, row.msg, logtime))
    elif cmdargs.nick:
        send('%s has never said %s.' % (cmdargs.nick, cmdargs.string))
    else:
        send('%s has never been said.' % cmdargs.string)
