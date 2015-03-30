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

from time import strftime, localtime
from helpers.orm import Log
from helpers.command import Command


@Command(['grep', 'loggrep'], ['config', 'db'])
def cmd(send, msg, args):
    """Greps the log for a string.
    Syntax: !grep <string>
    """
    if not msg:
        send('Please specify a search term.')
        return
    cmdchar = args['config']['core']['cmdchar']
    row = args['db'].query(Log).filter(Log.type == 'pubmsg', ~Log.msg.startswith(cmdchar), Log.msg.like('%'+msg+'%')).order_by(Log.id.desc()).first()
    if row:
        logtime = strftime('%Y-%m-%d %H:%M:%S', localtime(row.time))
        send("%s said %s at %s" % (row.source, row.msg, logtime))
    else:
        send('%s not found.' % msg)
