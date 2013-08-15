# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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

import json
from random import choice

args = ['srcdir']


def getquote(send, srcdir, msg):
    quotefile = srcdir + "/data/quotes"
    quotes = json.load(open(quotefile))
    if not msg:
        return choice(quotes)
    elif not msg.isdigit():
        send("Not a Number")
        return None
    elif int(msg) >= len(quotes):
        send("Invalid quote number.")
        return None
    else:
        return quotes[int(msg)]


def cmd(send, msg, args):
    """Returns a random quote.
    Syntax: !quote <number>
    """
    try:
        quote = getquote(send, args['srcdir'], msg)
        if quote:
            send(quote)
    except (OSError, IndexError):
        send("Nobody has taste in this channel.")
