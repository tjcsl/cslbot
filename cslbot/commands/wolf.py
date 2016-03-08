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

from lxml.etree import fromstring

from requests import get

from ..helpers.command import Command
from ..helpers.urlutils import get_short


@Command('wolf', ['config'])
def cmd(send, msg, args):
    """Queries WolframAlpha.

    Syntax: {command} <expression>

    """
    if not msg:
        send("Evaluate what?")
        return
    params = {'format': 'plaintext', 'reinterpret': 'true', 'input': msg, 'appid': args['config']['api']['wolframapikey']}
    req = get('http://api.wolframalpha.com/v2/query', params=params)
    if req.status_code == 403:
        send("WolframAlpha is having issues.")
        return
    xml = fromstring(req.content)
    output = xml.findall('./pod')
    key = args['config']['api']['googleapikey']
    url = get_short("http://www.wolframalpha.com/input/?i=%s" % msg, key)
    text = "No output found."
    for x in output:
        if 'primary' in x.keys():
            text = x.find('./subpod/plaintext').text
    if text is None:
        send("No Output parsable")
    else:
        # Only send the first three lines of output
        for t in text.splitlines()[:3]:
            send(t)
    send("See %s for more info" % url)
