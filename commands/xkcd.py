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

import json
from urllib.request import urlopen
from random import randrange
from helpers.command import Command


def get_num():
    data = json.loads(urlopen('http://xkcd.com/info.0.json').read().decode())
    return data['num']


@Command('xkcd')
def cmd(send, msg, args):
    """Gets a xkcd comic.
    Syntax: !xkcd <num|latest>
    """
    latest = get_num()
    if not msg:
        msg = randrange(1, latest)
    elif msg == 'latest':
        msg = latest
    elif msg.isdigit():
        msg = int(msg)
        if msg > latest or msg < 1:
            send("Number out of range")
            return
    else:
        send("Not A Valid Positive Integer")
        return
    url = 'http://xkcd.com/%d/info.0.json' % msg if msg != 'latest' else 'http://xkcd.com/info.0.json'
    data = json.loads(urlopen(url).read().decode())
    output = "%s -- http://xkcd.com/%d" % (data['safe_title'], data['num'])
    send(output)
