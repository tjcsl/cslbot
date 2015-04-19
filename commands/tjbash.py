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

from bs4 import BeautifulSoup
from requests import get
from random import choice
from helpers.command import Command


@Command('tjbash')
def cmd(send, msg, _):
    """Finds a random quote from tjbash.org given search criteria.
    Syntax: !tjbash [searchstring]
    """
    if len(msg) == 0:
        url = 'http://tjbash.org/random1'
    else:
        url = 'http://tjbash.org/search?query='
        targs = msg.split(' ')
        if len(targs) == 1 and targs[0].isnumeric():
            url = 'http://tjbash.org/' + targs[0]
        else:
            for tag in targs:
                url += 'tag:' + tag + ' '
    html = get(url)
    soup = BeautifulSoup(html.text)
    quotes = soup.findAll('blockquote')
    if len(quotes) < 1:
        send("There were no results.")
        return
    quote = choice(quotes)
    text = [x for x in quote.text.splitlines() if x]
    text = text[:3]
    for line in text:
        send(line.rstrip())
    root = quote.parent.parent
    postid = root.get('id').split('quote-')[1].rstrip()
    tagitems = root.find('div', attrs={'class': 'quote-tags'})
    if tagitems is not None:
        tagitems = tagitems.find_all('a')
        tags = []
        for tag in tagitems:
            tags.append(tag.text.rstrip())
        send(" -- {} -- {}http://tjbash.org/{}".format(', '.join(tags), "continued: " if (len(text) > 3) else "", postid))
    else:
        send(" -- http://tjbash.org/{}".format(postid))
