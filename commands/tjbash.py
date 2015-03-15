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

from bs4 import BeautifulSoup
from requests import get
from random import choice
from helpers.command import Command


@Command('tjbash')
def cmd(send, msg, args):
    """Finds a random quote from tjbash.org given search criteria
    """
    if len(args) < 2:
        url = 'http://tjbash.org/random'
    else:
        url = 'http://tjbash.org/search?query='
        for tag in args[1:]:
            url += 'tag:'+tag+' '
    html = get(url)
    soup = BeautifulSoup(html.text)
    quotes = soup.findAll('blockquote')
    if len(quotes) < 1:
        send("There were no results.")
        return
    send(str(quotes))
    quote = choice(quotes)
    text = quote.text.splitlines()
    text = list(filter(None, text))
    text = text[:3]
    for line in text:
        send(line)
    root = quote.parent.parent
    postid = root.get('id').split('quote-')[1]
    tagitems = root.find('div', attrs={'class':'quote-tags'})
    if tagitems is not None:
        tagitems = tagitems.find_all('a')
        tags = []
        for tag in tagitems:
            tags.append(tag.text)
        send(" -- {} -- http://tjbash.org/{}".format(', '.join(tags), postid))
    else:
        send(" -- http://tjbash.org/{}".format(postid))
