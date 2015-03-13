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

import re
from requests import get
from lxml.html import fromstring
from helpers.command import Command
from helpers.urlutils import get_short


@Command(['cve', 'cveid'], ['config'])
def cmd(send, msg, args):
    """Gets info on a CVE id from MITRE's CVE database
    Syntax: !cve <cveid>
    """
    elements = msg.split('-')
    if len(elements) > 3 or len(elements) < 2:
        send("Invalid CVE format")
        return
    # If there are three fields, ignore the first (we don't actually need to send CVE-
    if len(elements) == 3:
        if not elements[0].upper() == 'CVE':
            send("Invalid CVE format")
            return
        elements.pop(0)
    # The first digit field should be exactly four digits long, the second is 4+
    if not re.search("^[\d]{4}$", elements[0]) or not re.search("^[\d]{4,}$", elements[1]):
        send("Invalid CVE format")
        return
    search = "%s-%s" % (elements[0], elements[1])
    url = 'http://cve.mitre.org/cgi-bin/cvename.cgi?name=%s' % search
    html = fromstring(get(url).text)
    title = html.find(".//title").text.splitlines()[2]
    if title.startswith('ERROR'):
        output = 'Invalid CVE Number'
    else:
        key = args['config']['api']['googleapikey']
        output = "%s -- %s" % (title, get_short(url, key))
    send(output)
