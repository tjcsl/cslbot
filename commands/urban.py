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

from urllib.parse import quote
from urllib.request import urlopen
import json


def cmd(send, msg, args):
    if not msg:
        return
    # pfoley's private key -- do not abuse
    data = json.loads(urlopen('http://api.urbandictionary.com/v0/define?term=%s' % (quote(msg))).read().decode())
    try:
        definition = data['list'][0]['definition'].replace('\n', ' ')
        send(definition)
    except KeyError:
        send("UrbanDictionary doesn't have a answer for you.")
