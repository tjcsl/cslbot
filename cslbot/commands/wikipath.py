# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

from ..helpers import arguments
from ..helpers.command import Command


def gen_path(cmdargs):
    epoch = datetime.now().timestamp()
    params = {'a1': cmdargs.first, 'linktype': 1, 'a2': cmdargs.second, 'allowsideboxes': 1, 'submit': epoch}
    html = get('http://beta.degreesofwikipedia.com/', params=params).text
    path = fromstring(html).find('pre')
    if path is None:
        return False
    output = []
    for x in path.text.splitlines():
        if '=>' in x:
            output.append(x.split('=>')[1].strip())
    return " -> ".join(output)


def get_article():
    params = {'action': 'query', 'list': 'random', 'rnlimit': 1, 'rnnamespace': 0, 'format': 'json'}
    data = get('http://en.wikipedia.org/w/api.php', params=params).json()
    data = data['query']['random']
    return data[0]['title'].replace(' ', '_')


def check_article(name):
    params = {'format': 'json', 'action': 'query', 'list': 'search', 'srlimit': '1', 'srsearch': name}
    data = get('http://en.wikipedia.org/w/api.php', params=params).json()
    return data['query']['search']


@Command('wikipath', ['config'])
def cmd(send, msg, args):
    """Find a path between two wikipedia articles.

    Syntax: {command} [article] [article]

    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('first', nargs='?')
    parser.add_argument('second', nargs='?')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if not cmdargs.first:
        cmdargs.first = get_article()
    else:
        if not check_article(cmdargs.first):
            send("%s isn't a valid wikipedia article, fetching a random one..." % cmdargs.first)
            cmdargs.first = get_article()
    if not cmdargs.second:
        cmdargs.second = get_article()
    else:
        if not check_article(cmdargs.second):
            send("%s isn't a valid wikipedia article, fetching a random one..." % cmdargs.second)
            cmdargs.second = get_article()

    path = gen_path(cmdargs)
    if path:
        send(path.replace('_', ' '))
    else:
        send("No path found between %s and %s. Do you need to add more links?" % (cmdargs.first.replace('_', ' '), cmdargs.second.replace('_', ' ')))
