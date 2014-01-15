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

from time import time
from helpers.urlutils import get_title, get_short
from helpers.hook import Hook
import re


@Hook(types=['pubmsg', 'action'], args=['config', 'db'])
def handle(send, msg, args):
    """ Get titles for urls.

    | Generate a short url.
    | Get the page title.
    """
    # crazy regex to match urls
    match = re.search(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.]
                          [a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()
                          <>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*
                          \)|[^\s`!()\[\]{};:'\".,<>?....]))""", msg)
    if match:
        url = match.group(1)
        cursor = args['db'].get()
        title = get_title(url)
        cursor.execute('INSERT INTO urls VALUES(?,?,?)', (url, title, time()))
        if args['config']['feature']['linkread'] == "True":
            send('** %s - %s' % (title, get_short(url)))
