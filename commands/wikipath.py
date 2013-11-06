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

from datetime import datetime
from lxml.html import fromstring
from requests import get
from helpers.command import Command


def gen_path(msg):
    epoch = datetime.now().timestamp()
    params = {'a1': msg[0], 'linktype': 1, 'a2': msg[1], 'allowsideboxes': 1, 'submit': epoch}
    html = get('http://beta.degreesofwikipedia.com/', params=params).text
    path = fromstring(html).find('pre')
    if path is None:
        return False
    output = []
    for x in path.text.splitlines():
        if '=>' in x:
            output.append(x.split('=>')[1].strip())
    return " -> ".join(output)


def get_articles():
    params = {'action': 'query', 'list': 'random', 'rnlimit': 2, 'rnnamespace': 0, 'format': 'json'}
    data = get('http://en.wikipedia.org/w/api.php', params=params).json()
    data = data['query']['random']
    return [data[0]['title'].replace(' ', '_'), data[1]['title'].replace(' ', '_')]


@Command('wikipath')
def cmd(send, msg, args):
    """Find a path between two wikipedia articles.
    Syntax: !wikipath <article> <article>
    """
    msg = msg.split()
    if len(msg) != 2:
        msg = get_articles()
    path = gen_path(msg)
    if path:
        send(path.replace('_', ' '))
    else:
        send("No path found between %s and %s. Do you need to add more links?" % (msg[0], msg[1]))
