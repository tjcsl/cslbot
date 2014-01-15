# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from requests import get
from helpers.command import Command


@Command('urban')
def cmd(send, msg, args):
    """Gets a definition from urban dictionary.
    Syntax: !urban (#<num>) <term>
    """
    if not msg:
        send("Lookup what?")
        return
    msg = msg.split()
    index = msg[0][1:] if msg[0].startswith('#') else None
    term = " ".join(msg[1:]) if index is not None else " ".join(msg)
    req = get('http://api.urbandictionary.com/v0/define', params={'term': term})
    data = req.json()['list']
    if len(data) == 0:
        output = "UrbanDictionary doesn't have a answer for you."
    elif index is None:
        output = data[0]['definition']
    elif not index.isdigit() or int(index) >= len(data):
        output = "Invalid Index"
    else:
        output = data[int(index)]['output']
    output = output.replace('shit', '$#!+').replace('fuck', 'fsck')
    output = output.splitlines()[0]
    if len(output) > 256:
        output = output[:253] + "..."
    send(output)
