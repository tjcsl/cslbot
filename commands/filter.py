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


@Command('filter', ['handler', 'is_admin', 'nick', 'type'])
def cmd(send, msg, args):
    """Changes the output filter.
    Syntax: !filter <filter|show|list|reset|chain filter>
    """
    # FIXME: use argparse
    output_filters = {
        "hashtag": textutils.gen_hashtag,
        "fwilson": textutils.gen_fwilson,
        "creffett": textutils.gen_creffett,
        "slogan": textutils.gen_slogan,
        "insult": textutils.gen_insult,
        "morse": textutils.gen_morse,
        "removevowels": textutils.removevowels,
        "binary": textutils.gen_binary,
        "xkcd": textutils.do_xkcd_sub,
        "praise": textutils.gen_praise,
        "reverse": textutils.reverse,
        "lenny": textutils.gen_lenny,
        "yoda": textutils.gen_yoda,
        "gizoogle": textutils.gen_gizoogle,
        "cloud": textutils.gen_cloud
    }
    if args['type'] == 'privmsg':
        send('Ahamilto wants to know all about your doings!')
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
        send("Available filters are %s" % ", ".join(output_filters.keys()))
    elif msg == 'reset' or msg == 'passthrough' or msg == 'clear':
        if args['is_admin'](args['nick']):
            args['handler'].outputfilter = [lambda x: x]
            send("Okay!")
        else:
            send("Nope, not gonna do it!")
    elif msg.startswith('chain'):
        if args['is_admin'](args['nick']):
            next_filter = msg.split()[1]
            if next_filter in output_filters.keys():
                args['handler'].outputfilter.append(output_filters[next_filter])
                send("Okay!")
            else:
                send("Invalid filter.")
        else:
            send("Nope, not gonna do it.")
    elif msg in output_filters.keys():
        if args['is_admin'](args['nick']):
            args['handler'].outputfilter = [output_filters[msg]]
            send("Okay!")
        else:
            send("Nope, not gonna do it!")
    else:
        send("Invalid filter.")
