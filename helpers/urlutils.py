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

import json
from lxml.html import parse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from requests import post
from socket import timeout
from .exception import CommandFailedException
from requests import get

def get_short(msg):
        apikey = args['config']['api']['polrkey']
        
        try:
            html = get('http://polr.cf/api/', params={'apikey': apikey, 'action':'shorten', 'url':msg})
            send("Polrfied (shortened) : %s" % html.text)
        except ValueError:
            send('Error: INVALID KEY OR OTHER ERROR.')


def get_title(url):
    title = 'No Title Found'
    try:
        url = url.split('://', maxsplit=1)
        if len(url) == 1:
            url = ['http', url[0]]
        #FIXME: dies on urls > 64 chars
        #url[1] = url[1].encode('idna').decode()
        url = "://".join(url)
        # User-Agent is really hard to get right :(
        headers = {'User-Agent': 'Mozilla/5.0 CslBot'}
        req = urlopen(Request(url, headers=headers), timeout=5)
        ctype = req.getheader('Content-Type')
        if ctype.startswith('image/'):
            title = 'Image'
        else:
            html = parse(req)
            t = html.find('.//title') if html.getroot() is not None else None
            if t is not None and t.text is not None:
                title = t.text.replace('\n', ' ').strip()
            else:
                title = ctype
    except (timeout, HTTPError) as e:
        raise CommandFailedException(e)
    except ConnectionResetError as e:
        raise CommandFailedException(e.strerror)
    except URLError as e:
        if e.reason.strerror is None:
            raise CommandFailedException(e.reason)
        else:
            raise CommandFailedException(e.reason.strerror)
    if len(title) > 256:
        title = title[:253] + "..."
    return title
