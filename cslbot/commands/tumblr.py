# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from random import randint
from requests import get
from ..helpers import arguments
from ..helpers.command import Command


def validate_blogname(name):
    if "." not in name:
        name += ".tumblr.com"


@Command('tumblr', ['config'])
def cmd(send, msg, args):
    """Searches tumblr
    Syntax: {command} <blogname>
    """
    apikey = args['config']['api']['tumblrconsumer']
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('blogname', action=arguments.TumblrParser)
    cmdargs = parser.parse_args(msg)

    # First, get the number of posts
    response = get('http://api.tumblr.com/v2/blog/%s/posts' % cmdargs.blogname, params={'api_key': apikey, 'type': 'text'}).json()
    if response['meta']['status'] != 200:
        send(response['meta']['msg'])
        return
    postcount = response['response']['total_posts']
    # No random post functionality and we can only get 20 posts per API call, so pick a random offset to get the random post
    if postcount <= 1:
        send("No text posts found.")
        return
    offset = randint(0, postcount-1)
    response = get('http://api.tumblr.com/v2/blog/%s/posts' % cmdargs.blogname,
                   params={'api_key': apikey, 'offset': offset, 'limit': 1, 'type': 'text', 'filter': 'text'}).json()
    post = response['response']['posts'][0]['body']
    # Account for possibility of multiple lines
    for line in post.splitlines():
        send(line)
    # TODO: Implement posting functionality, need to figure out oauth
