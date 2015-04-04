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

from helpers import arguments
from helpers.command import Command


@Command('mode', ['nick', 'is_admin', 'handler', 'botnick', 'target', 'config'])
def cmd(send, msg, args):
    """Sets a mode.
    Syntax: !mode (--chan <chan>) <mode>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--chan', '--channel', action=arguments.ChanParser)
    try:
        cmdargs, extra = parser.parse_known_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.chan:
        target = cmdargs.chan
    else:
        target = args['target']
    mode = ' '.join(extra)
    if not mode:
        send("What mode?")
    if target == 'private':
        send("Modes don't work in a PM!")
    if not args['is_admin'](args['nick']):
        send("Admins only")
    if target not in args['handler'].channels:
        send("Bot not in channel " + target)
    if args['botnick'] not in list(args['handler'].channels[target].opers()):
        send("Bot must be opped in channel " + target)
    args['handler'].connection.mode(target, " %s" % mode)
    send("Mode \"%s\" on %s by %s" % (mode, target, args['nick']), target=args['config']['core']['ctrlchan'])
