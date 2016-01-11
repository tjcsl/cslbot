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

from ..helpers.command import Command
from ..helpers import arguments, textutils


def get_filters(handler, target):
    # Strip the gen_ from the names
    names = [x.__name__[4:] for x in handler.outputfilter[target]]
    if not names:
        names = ['passthrough']
    return "Current filter(s): %s" % ", ".join(names)


@Command('filter', ['config', 'target', 'handler', 'is_admin', 'nick', 'type'])
def cmd(send, msg, args):
    """Changes the output filter.
    Syntax: {command} [--channel channel] <filter|--show|--list|--reset|--chain filter,[filter2,...]>
    """
    if args['type'] == 'privmsg':
        send('Filters must be set in channels, not via private message.')
        return
    isadmin = args['is_admin'](args['nick'])
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--channel', nargs='?', default=args['target'])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('filter', nargs='?')
    group.add_argument('--show', action='store_true')
    group.add_argument('--list', action='store_true')
    group.add_argument('--reset', '--clear', action='store_true')
    group.add_argument('--chain')
    if not msg:
        send(get_filters(args['handler'], args['target']))
        return
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.list:
        send("Available filters are %s" % ", ".join(textutils.output_filters.keys()))
    elif cmdargs.reset and isadmin:
        args['handler'].outputfilter[cmdargs.channel].clear()
        send("Okay!")
    elif cmdargs.chain and isadmin:
        if not args['handler'].outputfilter[cmdargs.channel]:
            send("Must have a filter set in order to chain.")
            return
        filter_list, output = textutils.append_filters(cmdargs.chain)
        if filter_list is not None:
            args['handler'].outputfilter[cmdargs.channel].extend(filter_list)
        send(output)
    elif cmdargs.show:
        send(get_filters(args['handler'], cmdargs.channel))
    elif isadmin:
        # If we're just adding a filter without chain, blow away any existing filters.
        filter_list, output = textutils.append_filters(cmdargs.filter)
        if filter_list is not None:
            args['handler'].outputfilter[cmdargs.channel].clear()
            args['handler'].outputfilter[cmdargs.channel].extend(filter_list)
        send(output)
    else:
        send('This command requires admin privileges.')
