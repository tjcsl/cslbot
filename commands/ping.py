# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from time import time
from helpers.misc import recordping
from helpers.command import Command


@Command(['ping', 'ping6'], ['handler', 'target', 'config', 'nick', 'name'])
def cmd(send, msg, args):
    """Ping something.
    Syntax: !ping <target>
    """
    if not msg:
        msg = args['nick']
    channel = args['target'] if args['target'] != 'private' else args['nick']
    # CTCP PING
    if "." not in msg:
        args['handler'].connection.ctcp("PING", msg, " ".join(str(time()).split('.')))
        recordping(msg, channel)
        return
    try:
        answer = subprocess.check_output([args['name'], '-q', '-W', '1', '-c', '1', msg], stderr=subprocess.STDOUT)
        answer = answer.decode().splitlines()
        send(answer[0])
        send(answer[-2])
    except subprocess.CalledProcessError as e:
        if e.returncode == 2:
            send("ping: unknown host " + msg)
        elif e.returncode == 1:
            send(e.output.decode().splitlines()[-2])
