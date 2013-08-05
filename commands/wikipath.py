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


def get_articles():
    data = json.loads(urlopen('http://en.wikipedia.org/w/api.php?action=query&list=random&rnlimit=2&rnnamespace=0&format=json').read().decode('ascii', 'ignore'))
    data = data['query']['random']
    return [data[0]['title'].replace(' ', '_'), data[1]['title'].replace(' ', '_')]


def cmd(send, msg, args):
    msg = msg.split()
    if len(msg) != 2:
        msg = get_articles()
    path = gen_path(msg)
    if path:
        send(path.replace('_', ' '))
    else:
        send("No path found between %s and %s. Do you need to add more links?" % (msg[0], msg[1]))
