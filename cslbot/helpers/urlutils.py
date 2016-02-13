# -*- coding: utf-8 -*-
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

import re

from lxml.html import document_fromstring

from requests import exceptions, get, post

from . import misc
from .exception import CommandFailedException


def get_short(msg, key):
    if len(msg) < 20:
        return msg
    try:
        data = post('https://www.googleapis.com/urlshortener/v1/url', params={'key': key}, json=({'longUrl': msg}),
                    headers={'Content-Type': 'application/json'}).json()
    except exceptions.ConnectTimeout as e:
        # Sanitize the error before throwing it
        raise exceptions.ConnectTimeout(re.sub('key=.*', 'key=<removed>', str(e)))
    if 'error' in data:
        return msg
    else:
        return data['id']


def get_title(url):
    title = 'No Title Found'
    try:
        # User-Agent is really hard to get right :(
        headers = {'User-Agent': 'Mozilla/5.0 CslBot'}
        req = get(url, headers=headers, timeout=10)
        ctype = req.headers.get('Content-Type')
        if req.status_code != 200:
            title = 'HTTP Error %d: %s' % (req.status_code, req.reason)
        elif ctype is not None and ctype.startswith('image/'):
            title = 'Image'
        elif ctype is not None and ctype.startswith('video/'):
            title = 'Video'
        else:
            html = document_fromstring(req.content)
            t = html.find('.//title')
            # FIXME: is there a cleaner way to do this?
            if t is not None and t.text is not None:
                # Try to handle multiple types of unicode.
                try:
                    title = bytes(map(ord, t.text)).decode('utf-8')
                except (UnicodeDecodeError, ValueError):
                    title = t.text
                title = ' '.join(title.splitlines()).strip()
            # If we have no <title> element, but we have a Content-Type, fall back to that
            elif ctype is not None:
                title = ctype
            else:
                title = "Title Not Found"
    except exceptions.InvalidSchema:
        raise CommandFailedException('%s is not a supported url.' % url)
    except exceptions.MissingSchema:
        return get_title('http://%s' % url)
    title = misc.truncate_msg(title, 256)
    return title
