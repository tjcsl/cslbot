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
from urllib.parse import quote
from urllib.request import urlopen
from helpers.command import Command


@Command(['google', 'g'])
def cmd(send, msg, args):
    """Googles something.
    Syntax: !google <term>
    """
    if not msg:
        send("Google what?")
        return
    data = json.loads(urlopen('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s' % quote(msg)).read().decode())
    try:
        url = data['responseData']['results'][0]['url']
        send("Google says " + url)
    except IndexError:
        send("Google didn't say much")
