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
from helpers.command import Command
from helpers.urlutils import get_title

@Command(['google', 'g'])
def cmd(send, msg, args):
    """Googles something.
    Syntax: {command} <term>
    """
    if not msg:
        send("Google what?")
        return
    data = get('http://ajax.googleapis.com/ajax/services/search/web', params={'v': '1.0', 'q': msg}).json()
    results = data['responseData']['results']
    if len(results) == 0:
        send("Google didn't say much.")
    else:
        url = results[0]['unescapedUrl']
        title = get_title(url)
        if len(title) > 128:
            title = title[:125] + "..."
        send("Google says %s (Title: %s)" % (url, title))
