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

import json
from urllib.request import urlopen
from urllib.parse import quote


def cmd(send, msg, args):
        html = urlopen('http://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srlimit=1&srsearch=' + quote(msg))
        data = json.loads(html.read().decode())
        try:
            url = data['query']['search'][0]['title']
        except Exception:
            send("%s isn't important enough to have a wikipedia article." % msg)
            return
        url = url.replace(' ', '_')
        send('http://en.wikipedia.org/wiki/' + url)
