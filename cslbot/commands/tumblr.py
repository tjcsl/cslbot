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
from ..helpers.orm import Tumblrs
from ..helpers.web import post_tumblr


@Command('tumblr', ['config', 'is_admin', 'db', 'nick'])
def cmd(send, msg, args):
    """Searches tumblr
    Syntax: {command} <blogname> <--submit content|--random>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('blogname', action=arguments.TumblrParser)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--submit', nargs='*')
    group.add_argument('--random', action='store_true')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return

    if cmdargs.random:
        apikey = args['config']['api']['tumblrconsumerkey']
        # First, get the number of posts
        response = get('https://api.tumblr.com/v2/blog/%s/posts' % cmdargs.blogname, params={'api_key': apikey, 'type': 'text'}).json()
        postcount = response['response']['total_posts']
        if postcount <= 1:
            send("No text posts found.")
            return
        # No random post functionality and we can only get 20 posts per API call, so pick a random offset to get the random post
        offset = randint(0, postcount-1)
        response = get('https://api.tumblr.com/v2/blog/%s/posts' % cmdargs.blogname,
                       params={'api_key': apikey, 'offset': offset, 'limit': 1, 'type': 'text', 'filter': 'text'}).json()
        entry = response['response']['posts'][0]['body']
        # Account for possibility of multiple lines
        lines = entry.splitlines()
        for line in lines:
            send(line)

    elif cmdargs.submit:
        if not cmdargs.submit:
            send('Post what?')
            return
        if isinstance(cmdargs.submit, list):
            cmdargs.submit = ' '.join(cmdargs.submit)
        if args['is_admin']:
            send(post_tumblr(args['config'], cmdargs.blogname, cmdargs.submit)[0])
        else:
            row = Tumblrs(post=cmdargs.submit, submitter=args['nick'], nick=args['nick'], blogname=cmdargs.blogname)
            args['db'].add(row)
            args['db'].flush()
            send("New Tumblr Post: %s -- %s, Submitted by %s" % (cmdargs.submit, cmdargs.blogname, args['nick']), target=args['config']['core']['ctrlchan'])
            send("Issue submitted for approval.", target=args['nick'])
    else:
        send("Did not get an argument (choices are --random, --submit)")
