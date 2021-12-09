# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

from lxml import etree
from requests import get

from ..helpers import arguments
from ..helpers.command import Command


@Command(['zipcode', 'zip'], ['config'])
def cmd(send, msg, args):
    """Gets the location of a ZIP code
    Syntax: {command} (zipcode)
    Powered by STANDS4, www.stands4.com
    """
    uid = args['config']['api']['stands4uid']
    token = args['config']['api']['stands4token']
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('zipcode', action=arguments.ZipParser)
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return

    req = get("http://www.stands4.com/services/v2/zip.php", params={'uid': uid, 'tokenid': token, 'zip': cmdargs.zipcode})

    xml = etree.fromstring(req.content, parser=etree.XMLParser(recover=True))
    location = xml.find('location').text
    send(f"{cmdargs.zipcode}: {location}")
