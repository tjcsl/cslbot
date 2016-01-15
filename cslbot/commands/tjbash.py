# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import operator
from random import choice

from lxml.html import fromstring
from requests import get

from ..helpers.command import Command


@Command('tjbash')
def cmd(send, msg, _):
    """Finds a random quote from tjbash.org given search criteria.
    Syntax: {command} [searchstring]
    """
    if not msg:
        url = 'http://tjbash.org/random1.html'
        params = {}
    else:
        targs = msg.split()
        if len(targs) == 1 and targs[0].isnumeric():
            url = 'http://tjbash.org/%s' % targs[0]
            params = {}
        else:
            url = 'http://tjbash.org/search.html'
            params = {'query': 'tag:%s' % '+'.join(targs)}
    req = get(url, params=params)
    doc = fromstring(req.text)
    quotes = doc.find_class('quote-body')
    if not quotes:
        send("There were no results.")
        return
    quote = choice(quotes)
    lines = [x.strip() for x in map(operator.methodcaller('strip'), quote.itertext())]
    # Only send up to three lines.
    for line in lines[:4]:
        send(line)
    tags = quote.getparent().find_class('quote-tags')
    postid = quote.getparent().getparent().get('id').replace('quote-', '')
    if tags:
        tags = [x.text for x in tags[0].findall('.//a')]
        send(" -- {} -- {}http://tjbash.org/{}".format(', '.join(tags), "continued: " if (len(lines) > 3) else "", postid))
    else:
        send(" -- http://tjbash.org/{}".format(postid))
