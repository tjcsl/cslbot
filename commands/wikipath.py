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

from datetime import datetime
from lxml.html import parse
from urllib.request import urlopen
args = ['modules']


def gen_path(msg):
    epoch = datetime.now().timestamp()
    url = 'http://beta.degreesofwikipedia.com/?a1=%s&linktype=1&a2=%s&allowsideboxes=1&submit=%s' % (msg[0], msg[1], epoch)
    html = parse(urlopen(url))
    path = html.find('body/pre')
    if path is None:
        return False
    output = []
    for x in path.text.splitlines():
        if '=>' in x:
            output.append(x.split('=>')[1].strip())
    return " -> ".join(output)


def cmd(send, msg, args):
    msg = msg.split()
    if len(msg) != 2:
        send("Need two articles.")
        return
    path = gen_path(msg)
    if path:
        send(path.replace('_', ' '))
    else:
        send("No path found. Do you need to add more links?")
