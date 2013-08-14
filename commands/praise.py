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


def gen_praise(msg):
    html = urlopen('http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG', timeout=1).read().decode()
    return re.search('h2>(.*)</h2', html, re.DOTALL).group(1).strip().replace('\n\n', '\n').replace('\n', ' ')


def cmd(send, msg, args):
    """Praises something.
    Syntax: !praise <something>
    """
    if not msg:
        send("Praise what?")
        return
    praise = gen_praise(msg)
    while not praise:
        praise = gen_praise(msg)
    send('%s: %s' % (msg, praise))
