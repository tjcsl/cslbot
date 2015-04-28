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

from ..helpers import arguments
from ..helpers.command import Command


@Command('mode', ['nick', 'handler', 'botnick', 'target', 'config'], admin=True)
def cmd(send, msg, args):
    """Sets a mode.
    Syntax: {command} [--chan <chan>] <mode>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--chan', '--channel', action=arguments.ChanParser)
    try:
        cmdargs, extra = parser.parse_known_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    target = cmdargs.channels[0] if hasattr(cmdargs, 'channels') else args['target']
    mode = " ".join(extra)
    if not mode:
        send('Please specify a mode.')
    elif target == 'private':
        send("Modes don't work in a PM!")
    elif target not in args['handler'].channels:
        send("Bot not in channel %s" % target)
    elif args['botnick'] not in list(args['handler'].channels[target].opers()):
        send("Bot must be opped in channel %s" % target)
    else:
        args['handler'].connection.mode(target, mode)
        if args['target'] != args['config']['core']['ctrlchan']:
            send("Mode \"%s\" on %s by %s" % (mode, target, args['nick']), target=args['config']['core']['ctrlchan'])
