# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

import html
import re

from requests import get

from ..helpers.hook import Hook
from ..helpers.reddit import check_exists
from ..helpers.urlutils import get_short


@Hook('reddit', ['pubmsg', 'action'], ['config'])
def handle(send, msg, args):
    for match in re.finditer(r'(?:^|\s)/r/([\w|^/]*)\b', msg):
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
        output = html.unescape(output)
        key = args['config']['api']['bitlykey']
        if subreddit == 'random':
            output = "{} -- {} (/r/{})".format(output, get_short('http://reddit.com%s' % data['url'], key), data['display_name'])
        else:
            output = "{} -- {}".format(output, get_short('http://reddit.com/r/%s' % subreddit, key))
        send(output)
