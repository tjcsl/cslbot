# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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


def cmd(send, msg, args):
    if not msg:
        send("Ping what?")
        return
    try:
        answer = subprocess.check_output(['ping', '-q', '-W', '1', '-c', '1', msg])
        send(answer.decode().splitlines()[-2])
    except subprocess.CalledProcessError as e:
        if e.returncode == 2:
            send("ping: unknown host " + msg)
        elif e.returncode == 1:
            send(e.output.decode().splitlines()[-2])
