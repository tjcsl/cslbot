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

from helpers.command import Command
from helpers import textutils


@Command('filter', ['handler', 'nick', 'type'], admin=True)
def cmd(send, msg, args):
    """Changes the output filter.
    Syntax: !filter <filter|show|list|reset|chain filter>
    """
    # FIXME: use argparse
    if args['type'] == 'privmsg':
        send('Filters must be set in channels, not via private message.')
    elif not msg or msg == 'show':
        names = []
        for i in args['handler'].outputfilter:
            name = i.__name__
            if name == '<lambda>':
                name = 'passthrough'
            else:
                name = name[4:]
            names.append(name)
        send("Current filter(s): %s" % ", ".join(names))
    elif msg == 'list':
        send("Available filters are %s" % ", ".join(textutils.output_filters.keys()))
    elif msg == 'reset' or msg == 'passthrough' or msg == 'clear':
        args['handler'].outputfilter = [lambda x: x]
        send("Okay!")
    elif msg.startswith('chain'):
        if args['handler'].outputfilter[0].__name__ == '<lambda>':
            send("Must have a filter set in order to chain.")
            return
        next_filter = msg.split()[1]
        if next_filter in textutils.output_filters.keys():
            args['handler'].outputfilter.append(textutils.output_filters[next_filter])
            send("Okay!")
        else:
            send("Invalid filter.")
    elif msg in textutils.output_filters.keys():
        args['handler'].outputfilter = [textutils.output_filters[msg]]
        send("Okay!")
    else:
        send("Invalid filter.")
