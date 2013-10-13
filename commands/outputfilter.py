# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from commands.fwilson import gen_fwilson
from commands.creffett import gen_creffett
from commands.slogan import gen_slogan
from commands.insult import gen_insult


@Command(['outputfilter', 'filter'], ['handler', 'is_admin', 'nick'])
def cmd(send, msg, args):
    """Changes the output filter.
    Syntax: !filter <filter|list|reset>
    """
    output_filters = {
        "fwilson": gen_fwilson,
        "creffett": gen_creffett,
        "slogan": gen_slogan,
        "insult": gen_insult
        }
    if not msg:
        send("Which filter?")
    elif msg == 'list':
        send("Available filters are %s" % ", ".join(output_filters.keys()))
    elif msg == 'reset' or msg == 'passthrough':
        args['handler'].outputfilter = lambda x: x
        send("Okay!")
    elif msg in output_filters.keys():
        if args['is_admin'](args['nick']):
            args['handler'].outputfilter = output_filters[msg]
            send("Okay!")
        else:
            send("Nope, not gonna do it!")
    else:
        send("Invalid filter.")
