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

import json
import socket
import errno
from lxml.html import parse
from requests import get
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


def get_short(msg):
    # prevent escaping of http://
    if '//' in msg:
        msg = msg.split('//')[1]

    if len(msg) <= 13:
        return 'http://' + msg

    data = {'longUrl': msg}
    data = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = Request('https://www.googleapis.com/urlshortener/v1/url', data, headers)
    try:
        rep = urlopen(req, timeout=5).read().decode()
        short = json.loads(rep)
        return short['id']
    except HTTPError as e:
        if e.getcode() == 400:
            return 'http://' + msg
        else:
            raise e


def get_title(url):
    title = 'No Title Found'
    try:
        if not url.lower().startswith('http'):
            url = 'http://' + url
        shorturl = get_short(url)
        # Wikipedia doesn't like the default User-Agent, so we rip-off chrome
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36'})
        html = parse(urlopen(req, timeout=5))
        title = html.getroot().find(".//title").text.strip()
        # strip unicode
        title = title.encode('utf-8', 'ignore').decode().replace('\n', ' ')
    except URLError as ex:
        # website does not exist
        if hasattr(ex.reason, 'errno'):
            if ex.reason.errno == socket.EAI_NONAME or ex.reason.errno == errno.ENETUNREACH:
                pass
        else:
            return '%s: %s' % (type(ex).__name__, str(ex).replace('\n', ' '))
    # page does not contain a title
    except AttributeError:
        pass
    return '** %s - %s' % (title, shorturl)


def check_exists(subreddit):
    req = get('http://www.reddit.com/r/%s/about.json' % subreddit, headers={'User-Agent': 'CslBot/1.0'}, allow_redirects=False)
    return req.status_code == 200
