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

from requests import Session, exceptions, post

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

def parse_title(req, session):
    if req.status_code != 200:
        return 'HTTP Error %d: %s' % (req.status_code, req.reason)
    ctype = req.headers.get('Content-Type')
    if ctype is not None:
        if ctype.startswith('image/'):
            return 'Image'
        if ctype.startswith('video/'):
            return 'Video'
    # If we're going to parse the html, we need a get request.
    if req.request.method == 'HEAD':
        req = session.get(url, timeout=10)
    html = document_fromstring(req.content)
    t = html.find('.//title')
    # FIXME: is there a cleaner way to do this?
    if t is not None and t.text is not None:
        # Try to handle multiple types of unicode.
        try:
            title = bytes(map(ord, t.text)).decode('utf-8')
        except (UnicodeDecodeError, ValueError):
            title = t.text
        return ' '.join(title.splitlines()).strip()
    # If we have no <title> element, but we have a Content-Type, fall back to that
    return 'Title Not Found' if ctype is None else ctype

def get_title(url):
    try:
        with Session() as session:
            # User-Agent is really hard to get right :(
            session.headers.update({'User-Agent': 'Mozilla/5.0 CslBot'})
            req = session.head(url, allow_redirects=True, timeout=10)
            if req.status_code == 405:
                # Site doesn't support HEAD
                req = session.get(url, timeout=10)
            title = parse_title(req, session)
            # We not want overly-long titles.
            title = misc.truncate_msg(title, 256)
    except exceptions.InvalidSchema:
        raise CommandFailedException('%s is not a supported url.' % url)
    except exceptions.MissingSchema:
        return get_title('http://%s' % url)
    return title
