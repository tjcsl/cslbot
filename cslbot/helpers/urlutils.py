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

import json
import re
import socket
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from lxml.html import parse
from requests import post
from requests.exceptions import ConnectTimeout

from . import misc
from .exception import CommandFailedException


def get_short(msg, key):
    if len(msg) < 20:
        return msg
    try:
        data = post('https://www.googleapis.com/urlshortener/v1/url', params={'key': key}, data=json.dumps({'longUrl': msg}),
                    headers={'Content-Type': 'application/json'}, timeout=10).json()
    except ConnectTimeout as e:
        # Sanitize the error before throwing it
        raise ConnectTimeout(re.sub('key=.*', 'key=<removed>', str(e)))
    if 'error' in data:
        return msg
    else:
        return data['id']


def ensure_prefix(url):
    url = url.split('://', maxsplit=1)
    if len(url) == 1:
        url = ['http', url[0]]
    return "://".join(url)


def get_title(url):
    title = 'No Title Found'
    try:
        url = ensure_prefix(url)
        url = urlsplit(url)
        url = urlunsplit((url[0], url[1].encode('idna').decode(), url[2], url[3], url[4]))
        url = url.encode('ascii', 'replace').decode()
        # User-Agent is really hard to get right :(
        headers = {'User-Agent': 'Mozilla/5.0 CslBot'}
        req = urlopen(Request(url, headers=headers), timeout=10, context=ssl.create_default_context())
        ctype = req.getheader('Content-Type')
        if ctype is not None and ctype.startswith('image/'):
            title = 'Image'
        else:
            html = parse(req)
            t = html.find('.//title') if html.getroot() is not None else None
            if t is not None and t.text is not None:
                # Try to handle multiple types of unicode.
                try:
                    title = bytes(map(ord, t.text)).decode('utf-8')
                except (UnicodeDecodeError, ValueError):
                    title = t.text
                title = title.replace('\n', ' ').strip()
            elif ctype is not None:
                title = ctype
            else:
                title = "Title Not Found"
    except (socket.timeout, ssl.CertificateError) as e:
        raise CommandFailedException(e)
    except HTTPError as e:
        title = 'HTTP Error %d' % e.code
    except ConnectionResetError as e:
        raise CommandFailedException(e.strerror)
    except URLError as e:
        if not hasattr(e.reason, 'strerror') or e.reason.strerror is None:
            raise CommandFailedException(e.reason)
        else:
            raise CommandFailedException(e.reason.strerror)
    title = misc.truncate_msg(title, 256)
    return title
