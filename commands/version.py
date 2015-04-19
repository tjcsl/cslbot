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
from helpers.command import Command


@Command('version', ['config'])
def cmd(send, msg, args):
    """Check the git revison.
    Syntax: !version [check|master]
    """
    apiOutput = get('https://api.github.com/repos/%s/branches/master' % args['config']['api']['githubrepo']).json()
    gitdir = dirname(__file__) + "/../.git"
    try:
        version = subprocess.check_output(['git', '--git-dir=%s' % gitdir, 'show', '--format=oneline']).decode().split('\n')[0].split(' ')[0]
    except subprocess.CalledProcessError:
        send("Couldn't get the version.")
    if not msg:
        send(version)
        return
    if msg == 'master':
        send(apiOutput['commit']['sha'])
    elif msg == 'check':
        check = 'Same' if apiOutput['commit']['sha'] == version else 'Different'
        send(check)
    else:
        send('Invalid argument')
