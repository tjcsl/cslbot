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

from random import choice

from lxml import etree

from requests import get

from ..helpers import arguments
from ..helpers.command import Command


@Command('wisdom', ['config'])
def cmd(send, msg, args):
    """Gets words of wisdom
    Syntax: {command} (--author <author>|--search <topic>)
    Powered by STANDS4, www.stands4.com
    """
    uid = args['config']['api']['stands4uid']
    token = args['config']['api']['stands4token']
    parser = arguments.ArgParser(args['config'])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--author', action='store_true')
    group.add_argument('--search', action='store_true')
    parser.add_argument('query', nargs='*')

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return

    if cmdargs.author:
        if not cmdargs.query:
            send("No author specified")
            return
        searchtype = 'author'
    elif cmdargs.search:
        if not cmdargs.query:
            send("No search terms specified")
            return
        searchtype = 'search'
    else:
        searchtype = 'random'

    if cmdargs.query:
        cmdargs.query = ' '.join(cmdargs.query)
    req = get("http://www.stands4.com/services/v2/quotes.php", params={'uid': uid, 'tokenid': token, 'query': cmdargs.query, 'searchtype': searchtype})
    xml = etree.fromstring(req.content, parser=etree.XMLParser(recover=True))  # type: ignore
    if len(xml) == 0:
        send("No words of wisdom found")
        return
    entry = choice(xml)
    quote = entry.find('quote').text
    author = entry.find('author').text
    send("%s -- %s" % (quote, author))
