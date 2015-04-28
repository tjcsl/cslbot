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

import re
import subprocess
from time import time
from ..helpers.command import Command


@Command(['ping', 'ping6'], ['handler', 'target', 'config', 'nick', 'name'])
def cmd(send, msg, args):
    """Ping something.
    Syntax: {command} <target>
    """
    if not msg:
        send("Ping what?")
        return
    channel = args['target'] if args['target'] != 'private' else args['nick']
    # CTCP PING
    if "." not in msg and ":" not in msg:
        targets = set(msg.split())
        if len(targets) > 3:
            send("Please specify three or fewer people to ping.")
            return
        for target in targets:
            if not re.match(args['config']['core']['nickregex'], target):
                    send("Invalid nick %s" % target)
            else:
                args['handler'].ping_map[target] = channel
                args['handler'].connection.ctcp("PING", target, " ".join(str(time()).split('.')))
        return
    try:
        answer = subprocess.check_output([args['name'], '-W', '1', '-c', '1', msg], stderr=subprocess.STDOUT)
        answer = answer.decode().splitlines()
        send(answer[0])
        send(answer[1])
    except subprocess.CalledProcessError as e:
        if e.returncode == 2:
            send("ping: unknown host " + msg)
        elif e.returncode == 1:
            send(e.output.decode().splitlines()[-2])
