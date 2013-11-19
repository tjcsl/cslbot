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

import re
from requests import get
from helpers.command import Command
from helpers.urlutils import get_title
from helpers.misc import check_exists


@Command(['cve'], ['cveid'])
def cmd(send, msg, args):
    """Gets info on a CVE id from MITRE's CVE database
    Syntax: !cve <cveid>
    """
    elements = cveid.split('-')
    if len(elements) > 3 or len(elements) < 2:
        send("Invalid CVE format")
        return
    #If there are three fields, ignore the first (we don't actually need to send CVE-
    if len(elements) == 3:
        elements.pop(0)
    #The first digit field should be exactly four digits long, the second is 4+
    if not re.search("^[\d]{4}$", elements[0]) or not re.search("^[\d]{4,}$"):
        send("Invalid CVE format")
        return
    search = elements[0] + "-" + elements[1]
    req = get('http://cve.mitre.org/cgi-bin/cvename.cgi?name=%s' % search, headers={'User-Agent': 'CslBot/1.0'})
    send(get_title(req.url))
