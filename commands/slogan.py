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
import HTMLParser
args = ['modules']


def gen_slogan(msg):
        msg = msg.replace(' ', '%20')
        html = urlopen('http://www.sloganizer.net/en/outbound.php?slogan='
                       + msg, timeout=2).read().decode()
        return re.search('>(.*)<', html).group(1).replace('\\', '').strip()


def cmd(send, msg, args):
    if not msg:
        ret = lambda word: word
        msg = args['modules']['word'].cmd(ret, '', {})

    slogan = gen_slogan(msg)
    while not slogan:
        slogan = gen_slogan(msg)
    parser = HTMLParser.HTMLParser()
    send(parser.unescape(slogan))
