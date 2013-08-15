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
from urllib.request import urlopen, Request
from urllib.error import HTTPError


def get_short(msg):
    # prevent escaping of http://
    if '//' in msg:
        msg = msg.split('//')[1]

    if len(msg) <= 13:
        return 'http://' + msg

    data = {'longUrl': msg}
    data = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = Request('https://www.googleapis.com/urlshortener/v1/url', data, headers)
    try:
        rep = urlopen(req, timeout=5).read().decode()
        short = json.loads(rep)
        return short['id']
    except HTTPError as e:
        if e.getcode() == 400:
            return 'http://' + msg
        else:
            raise e


def cmd(send, msg, args):
    """Shortens the given url.
    Syntax: !short <url>
    """
    if not msg:
        send("Shorten what?")
        return
    send(get_short(msg))
