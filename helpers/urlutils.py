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

import errno
import json
from lxml.html import fromstring
from requests import get, post
from requests.exceptions import ConnectionError, Timeout


def get_short(msg):
    if len(msg) < 20:
        return msg
    data = post('https://www.googleapis.com/urlshortener/v1/url', data=json.dumps({'longUrl': msg}), headers={'Content-Type': 'application/json'}).json()
    if 'error' in data:
        return msg
    else:
        return data['id']


def get_title(url):
    title = 'No Title Found'
    try:
        if not url.startswith('http'):
            url = "http://%s" % url
        shorturl = get_short(url)
        # Wikipedia doesn't like the default User-Agent, so we rip-off chrome
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36'}
        req = get(url, headers=headers, timeout=2)
        html = fromstring(req.text.encode())
        t = html.find('.//title')
        if t is not None and t.text is not None:
            title = t.text.replace('\n', ' ').strip()
    except ConnectionError as ex:
        if ex.args[0].reason.errno != -errno.ENOENT:
            raise ex
    except Timeout:
        title = 'Request Timed Out'
    return '** %s - %s' % (title, shorturl)


def check_exists(subreddit):
    req = get('http://www.reddit.com/r/%s/about.json' % subreddit, headers={'User-Agent': 'CslBot/1.0'}, allow_redirects=False)
    return req.status_code == 200
