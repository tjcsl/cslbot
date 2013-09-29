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

from commands.short import get_short
from helpers.hook import Hook
import re
import socket
import errno
from lxml.html import parse
from urllib.request import urlopen, Request
from urllib.error import URLError


@Hook(types=['pubmsg', 'action'], args=['nick', 'do_kick', 'target'])
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
        try:
            url = match.group(1)
            if not url.startswith('http'):
                url = 'http://' + url
            shorturl = get_short(url)
            # Wikipedia doesn't like the default User-Agent
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0 Python-urllib/3.3'})
            html = parse(urlopen(req, timeout=5))
            title = html.getroot().find(".//title").text.strip()
            # strip unicode
            title = title.encode('utf-8', 'ignore').decode().replace('\n', ' ')
        except URLError as ex:
            # website does not exist
            if hasattr(ex.reason, 'errno'):
                if ex.reason.errno == socket.EAI_NONAME or ex.reason.errno == errno.ENETUNREACH:
                    return
            else:
                send('%s: %s' % (type(ex).__name__, str(ex).replace('\n', ' ')))
                return
        # page does not contain a title
        except AttributeError:
            title = 'No Title Found'
        send('** %s - %s' % (title, shorturl))
