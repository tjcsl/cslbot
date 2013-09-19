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

import subprocess
import json

args = ['srcdir']


def cmd(send, msg, args):
    """Evaluates mathmatical expressions.
    Syntax: !bc <expression>
    """
    if not msg:
        send("Calculate what?")
        return
    try:
        data = json.load(open(args['srcdir'] + "/data/score"))
        for u in data:
            msg = msg.replace(u, str(data[u]))
    except OSError:
        pass
    msg += '\n'
    proc = subprocess.Popen(['bc', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.communicate(msg.encode())[0]
    output = output.decode().strip().replace('\n', ' ')
    send(output)
