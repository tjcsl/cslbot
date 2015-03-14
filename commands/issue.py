# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from helpers.orm import Issues
from helpers.command import Command


def get_issues(repo):
    return get('https://api.github.com/repos/%s/issues' % repo).json()


def create_issue(msg, nick, repo, apikey):
    body = {"title": msg, "body": "Issue created by %s" % nick, "labels": ["bot"]}
    headers = {'Authorization': 'token %s' % apikey}
    req = post('https://api.github.com/repos/%s/issues' % repo, headers=headers, data=json.dumps(body))
    data = req.json()
    return data['html_url']


@Command(['issue', 'bug'], ['source', 'db', 'config', 'type', 'is_admin', 'nick'])
def cmd(send, msg, args):
    """Files a github issue or gets a open one.
    Syntax: !issue (description)
    """
    repo = args['config']['api']['githubrepo']
    apikey = args['config']['api']['githubapikey']
    if args['type'] == 'privmsg':
        send('You want to let everybody know about your problems, right?')
    elif msg.isdigit():
        issue = get('https://api.github.com/repos/%s/issues/%d' % (repo, int(msg))).json()
        if 'message' in issue:
            send("Invalid Issue Number")
        else:
            send("%s -- %s" % (issue['title'], issue['html_url']))
    elif not msg:
        issues = []
        n = 1
        while True:
            headers = {'Authorization': 'token %s' % apikey}
            page = get('https://api.github.com/repos/%s/issues' % repo, params={'per_page': '100', 'page': n}, headers=headers).json()
            n += 1
            if page:
                issues += page
            else:
                break
        issue = choice(issues)
        send("There are %d open issues, here's one." % len(issues))
        send("#%d -- %s -- %s" % (issue['number'], issue['title'], issue['html_url']))
    elif args['is_admin'](args['nick']):
        url = create_issue(msg, args['source'], repo, apikey)
        send("Issue created -- %s -- %s" % (url, msg))
    else:
        row = Issues(title=msg, source=args['source'])
        args['db'].add(row)
        args['db'].flush()
        send("New Issue: #%d -- %s, Submitted by %s" % (row.id, msg, args['nick']), target=args['config']['core']['ctrlchan'])
        send("Issue submitted for approval.", target=args['nick'])
