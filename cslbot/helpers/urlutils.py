# -*- coding: utf-8 -*-
# Copyright (C) 2013-2017 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import base64
import re
from contextlib import closing

from lxml.html import document_fromstring

from requests import Session, codes, exceptions, get, post

from . import misc
from .exception import CommandFailedException


class ImageException(Exception):
    pass


def get_short(msg, key):
    if len(msg) < 20:
        return msg
    try:
        with closing(
                post(
                    'https://www.googleapis.com/urlshortener/v1/url',
                    params={'key': key},
                    json=({
                        'longUrl': msg
                    }),
                    headers={'Content-Type': 'application/json'})) as req:
            data = req.json()
            return msg if 'error' in data else data['id']
    except exceptions.ConnectTimeout as e:
        # Sanitize the error before throwing it
        raise exceptions.ConnectTimeout(re.sub('key=.*', 'key=<removed>', str(e)))


def parse_title(req):
    max_size = 1024 * 256  # 256KB
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


def identify_image(req, key):
    img = get(req.url)
    encoded_data = base64.b64encode(img.content)
    req = post(
        "https://vision.googleapis.com/v1/images:annotate",
        params={'key': key},
        json=({
            'requests': [{
                'image': {
                    'content': encoded_data
                },
                'features': {
                    'type': 'LABEL_DETECTION',
                    'maxResults': 5
                }
            }]
        }),
        headers={'Content-Type': 'application/json'})
    data = req.json()
    if 'error' in data:
        raise ImageException(data['error'])
    response = data['responses'][0]
    labels = []
    for label in response.get('labelAnnotations', []):
        labels.append("{}: {:.2%}".format(label['description'], label['score']))
    if not labels:
        raise ImageException("No labels found")
    return labels


def parse_mime(req, key):
    ctype = req.headers.get('Content-Type')
    if ctype is None:
        return ctype
    ctype = ctype.split('/')
    if ctype[0] == 'audio':
        return 'Audio'
    if ctype[0] == 'image':
        try:
            labels = identify_image(req, key)
            return 'Image: {}'.format(', '.join(labels))
        except ImageException as ex:
            return "Image: {}".format(ex)
    if ctype[0] == 'video':
        return 'Video'
    if ctype[0] == 'application':
        if ctype[1] in ['zip', 'x-zip-compressed']:
            return 'Zip'
        if ctype[1] == 'octet-stream':
            return 'Octet Stream'
        if ctype[1] == 'pdf':
            return 'Pdf'
    return None


def get_title(url, key):
    title = None
    timeout = (5, 20)
    with closing(Session()) as session:
        # User-Agent is really hard to get right :(
        session.headers.update({'User-Agent': 'Mozilla/5.0 CslBot'})
        try:
            req = session.head(url, allow_redirects=True, verify=False, timeout=timeout)
            if req.status_code == codes.ok:
                title = parse_mime(req, key)
            # 405/501 mean this site doesn't support HEAD
            elif req.status_code not in [codes.not_allowed, codes.not_implemented]:
                title = 'HTTP Error %d: %s' % (req.status_code, req.reason)
        except exceptions.InvalidSchema:
            raise CommandFailedException('%s is not a supported url.' % url)
        except exceptions.MissingSchema:
            return get_title('http://%s' % url, key)
        # HEAD didn't work, so try GET
        if title is None:
            req = session.get(url, timeout=timeout, stream=True)
            if req.status_code == codes.ok:
                title = parse_mime(req, key) or parse_title(req)
            else:
                title = 'HTTP Error %d: %s' % (req.status_code, req.reason)
    if title is None:
        return 'Title Not Found'
    # We don't want overly-long titles.
    return misc.truncate_msg(title, 256)
