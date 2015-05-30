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
import socket
import ssl
import re
from lxml.html import parse
from urllib import request
from urllib.error import URLError, HTTPError
from urllib.parse import urlsplit, urlunsplit
from requests import post
from requests.exceptions import ConnectTimeout
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


def get_title(url):
    title = 'No Title Found'
    try:
        url = url.split('://', maxsplit=1)
        if len(url) == 1:
            url = ['http', url[0]]
        url = "://".join(url)
        url = urlsplit(url)
        url = urlunsplit((url[0], url[1].encode('idna').decode(), url[2], url[3], url[4]))
        # User-Agent is really hard to get right :(
        headers = {'User-Agent': 'Mozilla/5.0 CslBot'}
        # We don't care if the cert is valid or not.
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        # FIXME: use urlopen(context=context) once 3.4.3 is released to travis.
        opener = request.build_opener(request.HTTPSHandler(context=context))
        req = opener.open(request.Request(url, headers=headers), timeout=10)
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
    except socket.timeout as e:
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
    # FIXME: handle unicode properly
    # Truncate over-long titles.
    if len(title) > 256:
        title = title[:253] + "..."
    return title
