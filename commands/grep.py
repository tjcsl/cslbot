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

import argparse
from time import strftime, localtime
from helpers.orm import Log
from helpers import arguments
from helpers.exception import NickException
from helpers.command import Command


@Command(['grep', 'loggrep'], ['config', 'db'])
def cmd(send, msg, args):
    """Greps the log for a string.
    Syntax: !grep (--nick <nick>) <string>
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--nick', action=arguments.NickParser)
    parser.add_argument('string', nargs='?', default=None)
    try:
        cmdargs = arguments.parse_args(parser, args['config'], msg)
    except NickException as e:
        send('%s is not a valid nick.' % e)
        return
    if not cmdargs.string:
        send('Please specify a search term.')
        return
    cmdchar = args['config']['core']['cmdchar']
    if cmdargs.nick:
        row = args['db'].query(Log).filter(Log.type == 'pubmsg', Log.source == cmdargs.nick, ~Log.msg.startswith(cmdchar),
                                           Log.msg.like('%'+cmdargs.string+'%')).order_by(Log.id.desc()).first()
    else:
        row = args['db'].query(Log).filter(Log.type == 'pubmsg', ~Log.msg.startswith(cmdchar), Log.msg.like('%'+cmdargs.string+'%')).order_by(Log.id.desc()).first()
    if row:
        logtime = strftime('%Y-%m-%d %H:%M:%S', localtime(row.time))
        send("%s said %s at %s" % (row.source, row.msg, logtime))
    elif cmdargs.nick:
        send('%s has never said %s.' % (cmdargs.nick, cmdargs.string))
    else:
        send('%s has never been said.' % cmdargs.string)
