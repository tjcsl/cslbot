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
from config import GITHUBAPIKEY
from urllib.request import urlopen, Request


def create_issue(msg):
    url = 'https://api.github.com/repos/fwilson42/ircbot/issues'
    req = Request(url)
    req.data = json.dumps({"title": msg}).encode()
    req.add_header('Authorization', 'token %s' % GITHUBAPIKEY)
    data = json.loads(urlopen(req).read().decode())
    return data['html_url']


def cmd(send, msg, args):
    issue = create_issue(msg)
    send("Issue Created -- %s" % issue)
