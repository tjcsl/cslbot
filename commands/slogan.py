# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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
from urllib.request import urlopen
from urllib.parse import quote
from html.entities import entitydefs
args = ['modules']


def gen_slogan(msg):
    msg = quote(msg)
    html = urlopen('http://www.sloganizer.net/en/outbound.php?slogan='
                   + msg, timeout=2).read().decode()
    slogan = re.search('>(.*)<', html).group(1).replace('\\', '').strip()
    slogan = ''.join(c for c in slogan if ord(c) > 31 and ord(c) < 127)
    slogan = slogan.replace('%20', ' ')
    if not slogan:
        return gen_slogan(msg)
    for c in entitydefs:
        slogan = slogan.replace('&%s;' % c, entitydefs[c])
    return slogan.replace('&amp;', '&')


def cmd(send, msg, args):
    """Gets a slogan.
    Syntax: !slogan <text>
    """
    if not msg:
        msg = args['modules']['word'].gen_word()
    slogan = gen_slogan(msg)
    send(slogan)
