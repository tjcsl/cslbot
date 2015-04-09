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

from requests import get
from helpers.command import Command


@Command(['google', 'g'], ['config'])
def cmd(send, msg, args):
    """Googles something.
    Syntax: !google <term>
    """
    if not msg:
        send("Google what?")
        return
    key = args['config']['api']['googleapikey']
    cx = args['config']['api']['googlesearchid']
    data = get('https://www.googleapis.com/customsearch/v1', params={'key': key, 'cx': cx, 'q': msg}).json()
    if 'items' not in data:
        send("Google didn't say much.")
    else:
        url = data['items'][0]['link']
        send("Google says %s" % url)
