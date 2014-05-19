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

import re
from time import localtime, strftime
from helpers.orm import Log
from helpers.command import Command


def get_last(cursor, nick):
    return cursor.query(Log).filter(Log.source.ilike(nick), Log.type != 'join').order_by(Log.time.desc()).first()


@Command('highlight', ['db', 'nick', 'config', 'target', 'botnick'])
def cmd(send, msg, args):
    """When a nick was last pinged.
    Syntax: {command} (nick)
    """
    if not msg:
        msg = args['nick']
    if not re.match(args['config']['core']['nickregex'], msg):
        send("Invalid nick.")
        return
    row = args['db'].query(Log).filter(Log.msg.ilike("%" + msg + "%"), ~Log.msg.contains('%shighlight' % args['config']['core']['cmdchar']),
                                       Log.target == args['target'], Log.source != args['botnick'], Log.source != msg,
                                       Log.type != 'mode', Log.type != 'nick').order_by(Log.time.desc()).first()
    if row is None:
        send("%s has never been pinged." % msg)
    else:
        time = strftime('%Y-%m-%d %H:%M:%S', localtime(row.time))
        send("<%s> %s: %s" % (time, row.source, row.msg))
