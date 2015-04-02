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

import re
from helpers.command import Command


def set_mode(args, mode):
    chanmatch = re.match('^#\w+', mode)
    if chanmatch:
        target = chanmatch.group(0)
        # Remove the channel name from the mode string
        mode = mode.split(' ', 1)[1]
    else:
        target = args['target']
    if not mode:
        return "What mode?"
    if target == 'private':
        return "Modes don't work in a PM!"
    if not args['is_admin'](args['nick']):
        return "Admins only"
    if target not in args['handler'].channels:
        return "Bot not in channel " + target
    if args['botnick'] not in list(args['handler'].channels[target].opers()):
        return "Bot must be opped in channel " + target
    args['handler'].connection.mode(target, " %s" % mode)
    return ""


@Command('mode', ['nick', 'is_admin', 'handler', 'botnick', 'target'])
def cmd(send, msg, args):
    """Sets a mode.
    Syntax: !mode [channel] <mode>
    """
    send(set_mode(args, msg))
