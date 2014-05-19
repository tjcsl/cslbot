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

from requests import get
from lxml.html import fromstring
from helpers.command import Command


def gen_praise(msg):
    html = fromstring(get('http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG').text)
    return html.find('body/center/h2').text.replace('\n', ' ').strip()


@Command('praise')
def cmd(send, msg, args):
    """Praises something.
    Syntax: {command} <something>
    """
    if not msg:
        send("Praise what?")
        return
    praise = gen_praise(msg)
    while not praise:
        praise = gen_praise(msg)
    send('%s: %s' % (msg, praise))
