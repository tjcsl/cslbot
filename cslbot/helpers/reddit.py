# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import time

from requests import get

from .urlutils import get_short, get_title


def check_exists(subreddit):
    """Make sure that a subreddit actually exists."""
    req = get('http://www.reddit.com/r/%s/about.json' % subreddit, headers={'User-Agent': 'CslBot/1.0'})
    if req.json().get('kind') == 'Listing':
        # no subreddit exists, search results page is shown
        return False
    return req.status_code == 200


def random_post(subreddit, apikey):
    """Gets a random post from a subreddit and returns a title and shortlink to it."""
    subreddit = '/r/random' if subreddit is None else '/r/%s' % subreddit
    urlstr = 'http://reddit.com%s/random?%s' % (subreddit, time.time())
    url = get(urlstr, headers={'User-Agent': 'CslBot/1.0'}).url
    return '** %s - %s' % (get_title(url), get_short(url, apikey))
