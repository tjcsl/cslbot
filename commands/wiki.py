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

from requests import get
from helpers.command import Command


@Command(['wiki', 'wikipedia', 'livedoc'], ['name'])
def cmd(send, msg, args):
    """Returns the first wikipedia result for the argument.
    Syntax: !wiki <term>
    """
    if not msg:
        send("Need a article.")
        return
    if 'livedoc' in args['name']:
        url = 'http://www.tjhsst.edu/admin/livedoc/index.php'
        name = 'livedoc'
    else:
        url = 'http://en.wikipedia.org/w'
        name = 'wikipedia'
    params = {'format': 'json', 'action': 'query', 'list': 'search', 'srlimit': '1', 'srsearch': msg}
    data = get('%s/api.php' % url, params=params).json()
    try:
        article = data['query']['search'][0]['title']
    except IndexError:
        send("%s isn't important enough to have a %s article." % (msg, name))
        return
    article = article.replace(' ', '_')
    # wikipedia uses /w for api and /wiki for articles
    if 'livedoc' not in args['name']:
        url += 'iki'
    send('%s/%s' % (url, article))
