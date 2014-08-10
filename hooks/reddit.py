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

import re
from requests import get
from helpers.hook import Hook
from helpers.misc import check_exists
from helpers.urlutils import get_short


@Hook(['pubmsg', 'action'])
def handle(send, msg, args):
    match = re.search(r'(?:^|\s)/r/([\w|^/]*)\b', msg)
    if not match:
        return
    subreddit = match.group(1)
    if not check_exists(subreddit):
        return
    data = get('http://reddit.com/r/%s/about.json' % subreddit, headers={'User-Agent': 'CslBot/1.0'}).json()['data']
    output = ''
    if data['public_description']:
        for line in data['public_description'].splitlines():
            output += line + " "
    elif data['description']:
        output += data['description'].splitlines()[0]
    else:
        output += data['display_name']
    output = output.strip()
    if len(output) > 256:
        output = output[:253] + "..."
    output = "%s -- %s" % (output, get_short('http://reddit.com/r/%s' % (subreddit)))
    send(output)
