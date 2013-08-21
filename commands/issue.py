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
from urllib.request import urlopen, Request

args = ['source', 'issues', 'connection', 'config']


def create_issue(msg, nick, repo, apikey):
    url = 'https://api.github.com/repos/%s/issues' % repo
    req = Request(url)
    req.data = json.dumps({"title": msg, "body": "Issue created by %s" % nick}).encode()
    req.add_header('Authorization', 'token %s' % apikey)
    data = json.loads(urlopen(req).read().decode())
    return data['html_url']


def cmd(send, msg, args):
    """Files a github issue.
    Syntax: !issue <description>
    """
    args['issues'].append([msg, args['source']])
    args['connection'].privmsg(args['config'].get('core', 'ctrlchan'), "New Issue: #%d -- %s" % (len(args['issues']) - 1, msg))
    send("Issue submitted for approval.")
