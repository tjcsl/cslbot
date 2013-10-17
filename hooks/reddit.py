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

import json
import re
from urllib.request import urlopen
from helpers.hook import Hook


def check_exists(subreddit):
    data = json.loads(urlopen('http://reddit.com/subreddits/search.json?q=%s' % subreddit).read().decode())
    return len(data['data']['children']) > 0


@Hook(types=['pubmsg', 'action'], args=[])
def handle(send, msg, args):
    match = re.search('/r/([\w]*)', msg)
    if not match:
        return
    subreddit = match.group(1)
    if not check_exists(subreddit):
        return
    data = urlopen('http://reddit.com/r/%s/about.json' % subreddit).read().decode()
    data = json.loads(data)['data']
    send(data['public_description'])
