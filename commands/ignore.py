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

from helpers import arguments
from helpers.command import Command


@Command('ignore', ['config', 'handler'], admin=True)
def cmd(send, msg, args):
    """Handles ignoring/unignoring people
    Syntax: !ignore <--clear|--show/--list|--delete|nick>
    """
    parser = arguments.ArgParser(args['config'])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--clear', action='store_true')
    group.add_argument('--show', '--list', action='store_true')
    group.add_argument('--delete', action='store_true')
    parser.add_argument('nick', nargs='?')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.clear:
        args['handler'].ignored.clear()
        send("Ignore list cleared.")
    elif cmdargs.show:
        if args['handler'].ignored:
            send(", ".join(args['handler'].ignored))
        else:
            send("Nobody is ignored.")
    elif cmdargs.delete:
        if not cmdargs.nick:
            send("Unignore who?")
        elif cmdargs.nick not in args['handler'].ignored:
            send("%s is not ignored." % cmdargs.nick)
        else:
            args['handler'].ignored.remove(cmdargs.nick)
            send("%s is no longer ignored." % cmdargs.nick)
    elif cmdargs.nick:
        args['handler'].ignore(send, cmdargs.nick)
    else:
        send("Ignore who?")
