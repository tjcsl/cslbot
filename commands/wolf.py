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

from urllib.request import urlopen
from urllib.parse import quote
from xml.etree import ElementTree
from helpers.command import Command
from commands.short import get_short


@Command('wolf', ['config'])
def cmd(send, msg, args):
    """Queries WolframAlpha.
    Syntax: !wolf <expression>
    """
    if not msg:
        send("Evaluate what?")
        return
    xml = urlopen('http://api.wolframalpha.com/v2/query?format=plaintext&reinterpret=true&input=%s&appid=%s' % (quote(msg), args['config']['api']['wolframapikey']))
    xml = ElementTree.parse(xml)
    output = xml.findall('./pod')
    url = get_short("http://www.wolframalpha.com/input/?i=%s" % msg)
    text = ["No output found."]
    for x in output:
        if 'primary' in x.keys():
            text = x.find('./subpod/plaintext').text.split('\n')
    for t in text:
        send(t)
    send("See %s for more info" % url)
