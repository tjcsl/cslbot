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
from requests import post, get
from random import choice
from helpers.command import Command


def get_issues(repo):
    return get('https://api.github.com/repos/%s/issues' % repo).json()


def create_issue(msg, nick, repo, apikey):
    body = {"title": msg, "body": "Issue created by %s" % nick, "labels": ["bot"]}
    headers = {'Authorization': 'token %s' % apikey}
    req = post('https://api.github.com/repos/%s/issues' % repo, headers=headers, data=json.dumps(body))
    data = req.json()
    return data['html_url']


@Command(['issue', 'bug'], ['source', 'issues', 'config', 'type', 'is_admin', 'nick'])
def cmd(send, msg, args):
    """Files a github issue or gets a open one.
    Syntax: !issue (description)
    """
    repo = args['config']['api']['githubrepo']
    if args['type'] == 'privmsg':
        send('You want to let everybody know about your problems, right?')
    elif not msg:
        issue = choice(get_issues(repo))
        send("#%d -- %s -- %s" % (issue['number'], issue['title'], issue['html_url']))
    elif args['is_admin'](args['nick']):
        url = create_issue(msg, args['source'], repo, args['config']['api']['githubapikey'])
        send("Issue created -- %s -- %s" % (url, msg))
    else:
        args['issues'].append([msg, args['source']])
        send("New Issue: #%d -- %s" % (len(args['issues']) - 1, msg), target=args['config']['core']['ctrlchan'])
        send("Issue submitted for approval.", target=args['nick'])
