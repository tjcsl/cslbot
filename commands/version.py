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

import subprocess
from os.path import dirname
from requests import get
from helpers import arguments
from helpers.command import Command


@Command('version', ['config'])
def cmd(send, msg, args):
    """Check the git revison.
    Syntax: {command} [check|master]
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('action', choices=['check', 'master', 'commit'], nargs='?')

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    apiOutput = get('https://api.github.com/repos/%s/branches/master' % args['config']['api']['githubrepo']).json()
    gitdir = dirname(__file__) + "/../.git"
    try:
        commit = subprocess.check_output(['git', '--git-dir=%s' % gitdir, 'rev-parse', 'HEAD']).decode().splitlines()[0]
        version = subprocess.check_output(['git', '--git-dir=%s' % gitdir, 'describe', '--tags']).decode()
    except subprocess.CalledProcessError:
        send("Couldn't get the version.")
    if not cmdargs.action:
        send(version)
        return
    if cmdargs.action == 'master':
        send(apiOutput['commit']['sha'])
    elif cmdargs.action == 'check':
        check = 'Same' if apiOutput['commit']['sha'] == commit else 'Different'
        send(check)
    elif cmdargs.action == 'commit':
        send(commit)
