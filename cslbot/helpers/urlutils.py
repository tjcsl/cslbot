# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
from contextlib import closing

from lxml.html import document_fromstring

from requests import Session, codes, exceptions, post

from . import misc
from .exception import CommandFailedException


def get_short(msg, key):
    if len(msg) < 20:
        return msg
    try:
        with closing(post('https://www.googleapis.com/urlshortener/v1/url',
                          params={'key': key},
                          json=({'longUrl': msg}),
                          headers={'Content-Type': 'application/json'})) as req:
            data = req.json()
            return msg if 'error' in data else data['id']
    except exceptions.ConnectTimeout as e:
        # Sanitize the error before throwing it
        raise exceptions.ConnectTimeout(re.sub('key=.*', 'key=<removed>', str(e)))


def parse_title(req):
    max_size = 1024 * 32  # 32KB
    req.raw.decode_content = True
    content = req.raw.read(max_size + 1)
    # FIXME: https://github.com/kennethreitz/requests/issues/2963
    if req.raw._connection is not None:
        req.raw._connection.close()
    ctype = req.headers.get('Content-Type')
    html = document_fromstring(content)
    t = html.find('.//title')
    # FIXME: is there a cleaner way to do this?
    if t is not None and t.text is not None:
        # Try to handle multiple types of unicode.
        try:
            title = bytes(map(ord, t.text)).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            title = t.text
        return ' '.join(title.splitlines()).strip()
    if len(content) > max_size:
        return 'Response Too Large: %s' % ctype
    # If we have no <title> element, but we have a Content-Type, fall back to that
    return ctype


def parse_mime(req):
    ctype = req.headers.get('Content-Type')
    if ctype is None:
        return ctype
    ctype = ctype.split('/')
    if ctype[0] == 'image':
        return 'Image'
    if ctype[0] == 'video':
        return 'Video'
    if ctype[0] == 'application':
        if ctype[1] == 'zip':
            return 'Zip'
        if ctype[1] == 'octet-stream':
            return 'Octet Stream'
    return None


def get_title(url):
    title = None
    with closing(Session()) as session:
        # User-Agent is really hard to get right :(
        session.headers.update({'User-Agent': 'Mozilla/5.0 CslBot'})
        try:
            req = session.head(url, allow_redirects=True, timeout=10)
            if req.status_code == codes.ok:
                title = parse_mime(req)
            # 405 means this site doesn't support HEAD
            elif req.status_code != codes.not_allowed:
                title = 'HTTP Error %d: %s' % (req.status_code, req.reason)
        except exceptions.InvalidSchema:
            raise CommandFailedException('%s is not a supported url.' % url)
        except exceptions.MissingSchema:
            return get_title('http://%s' % url)
        # HEAD didn't work, so try GET
        if title is None:
            req = session.get(url, timeout=10, stream=True)
            if req.status_code == codes.ok:
                title = parse_mime(req) or parse_title(req)
            else:
                title = 'HTTP Error %d: %s' % (req.status_code, req.reason)
    if title is None:
        return 'Title Not Found'
    # We don't want overly-long titles.
    return misc.truncate_msg(title, 256)
