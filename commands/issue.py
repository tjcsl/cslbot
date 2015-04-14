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

import json
from requests import post, get
from random import choice
from helpers import arguments
from helpers.orm import Issues
from helpers.command import Command


def create_issue(cmdargs, nick, repo, apikey):
    body = {"title": cmdargs.title, "body": "%s\nIssue created by %s" % (cmdargs.desc, nick), "labels": ["bot"]}
    headers = {'Authorization': 'token %s' % apikey}
    req = post('https://api.github.com/repos/%s/issues' % repo, headers=headers, data=json.dumps(body))
    data = req.json()
    return data['html_url']


@Command(['issue', 'bug'], ['source', 'db', 'config', 'type', 'is_admin', 'nick'])
def cmd(send, msg, args):
    """Files a github issue or gets a open one.
    Syntax: !issue (--create title (--desc description)) (--get number)
    """
    repo = args['config']['api']['githubrepo']
    apikey = args['config']['api']['githubapikey']
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--get', action='store_true')
    parser.add_argument('title', nargs='?')
    parser.add_argument('--desc', '--description', nargs='+', default="No description given")
    cmdargs = parser.parse_args(msg)
    print(cmdargs)
    cmdargs.title = ' '.join(cmdargs.title) if cmdargs.title is not None else ''
    cmdargs.desc = ' '.join(cmdargs.desc) if cmdargs.desc is not None else ''
    if args['type'] == 'privmsg':
        send('You want to let everybody know about your problems, right?')
    elif cmdargs.get or cmdargs.title.isdigit():
        issue = get('https://api.github.com/repos/%s/issues/%d' % (repo, int(title))).json()
        if 'message' in issue:
            send("Invalid Issue Number")
        else:
            send("%s -- %s" % (issue['title'], issue['html_url']))
    elif not cmdargs.title:
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
        if len(issues) == 0:
            send("No open issues to choose from!")
        else:
            issue = choice(issues)
            num_issues = len([x for x in issues if 'pull_request' not in x])
            send("There are %d open issues, here's one." % num_issues)
            send("#%d -- %s -- %s" % (issue['number'], issue['title'], issue['html_url']))
    elif cmdargs.create and args['is_admin'](args['nick']):
        url = create_issue(cmdargs, args['source'], repo, apikey)
        send("Issue created -- %s -- %s -- %s" % (url, cmdargs.title, cmdargs.desc))
    elif cmdargs.create:
        row = Issues(title=cmdargs.title, desc=cmdargs.desc, source=args['source'])
        args['db'].add(row)
        args['db'].flush()
        send("New Issue: #%d -- %s -- %s, Submitted by %s" % (row.id, cmdargs.title, cmdargs.desc, args['nick']), target=args['config']['core']['ctrlchan'])
        send("Issue submitted for approval.", target=args['nick'])
    else:
        send("Invalid arguments -- did you forget to set --create or --get?")
