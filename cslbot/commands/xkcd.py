# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from random import randrange

from requests import get

from ..helpers.command import Command


def get_latest():
    return get('http://xkcd.com/info.0.json').json()['num']


def do_search(msg, key, searchid):
    params = {'q': msg, 'key': key, 'cx': searchid}
    data = get('https://www.googleapis.com/customsearch/v1', params=params).json()
    if 'items' not in data:
        output = "No Results found."
    else:
        data = data['items'][0]
        output = "%s -- %s" % (data['title'], data['link'])
    return output


@Command('xkcd', ['config'])
def cmd(send, msg, args):
    """Gets a xkcd comic.

    Syntax: {command} [num|latest|term]

    """
    latest = get_latest()
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
        send(do_search(msg, args['config']['api']['googleapikey'], args['config']['api']['xkcdsearchid']))
        return
    url = 'http://xkcd.com/%d/info.0.json' % msg if msg != 'latest' else 'http://xkcd.com/info.0.json'
    data = get(url).json()
    output = "%s -- http://xkcd.com/%d" % (data['safe_title'], data['num'])
    send(output)
