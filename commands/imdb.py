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

from requests import get
from lxml.html import fromstring
from helpers.urlutils import get_short
from helpers.command import Command


@Command(['movie', 'imdb'])
def cmd(send, msg, args):
    """Gets a random movie.
    Syntax: !movie
    """

    req = get('http://www.imdb.com/random/title')
    html = fromstring(req.text)
    name = html.find('head/title').text.split('-')[0].strip()
    send("%s -- %s" % (name, get_short(req.url)))
