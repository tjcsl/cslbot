# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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


@Command('define', ['config'])
def cmd(send, msg, args):
    """Gets the definition of a word
    Syntax: {command} (word)
    Powered by STANDS4, www.stands4.com
    """
    uid = args['config']['api']['stands4uid']
    token = args['config']['api']['stands4token']
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--entry', type=int, default=0, nargs='?')
    parser.add_argument('word', nargs='+')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    cmdargs.word = ' '.join(cmdargs.word)

    req = get("http://www.stands4.com/services/v2/defs.php", params={'uid': uid, 'tokenid': token, 'word': cmdargs.word})
    xml = etree.fromstring(req.content, parser=etree.XMLParser(recover=True))
    if len(xml) == 0:
        send("No results found for %s" % cmdargs.word)
        return
    if cmdargs.entry >= len(xml):
        send("Invalid index %d for term %s" % (cmdargs.entry, cmdargs.word))
        return
    term = xml[cmdargs.entry].find('term').text
    definition = xml[cmdargs.entry].find('definition').text
    definition = ' '.join(definition.splitlines()).strip()
    send("%s: %s" % (term, definition))
