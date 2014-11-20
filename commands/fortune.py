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
import re
from random import random
from helpers.command import Command


def get_list(offensive=False):
    cmd = ['fortune', '-f']
    if offensive:
        cmd.append('-o')
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
    output = re.sub('[0-9]{1,2}\.[0-9]{2}%', '', output)
    fortunes = [x.strip() for x in output.splitlines()[1:]]
    if offensive:
        fortunes = map(lambda x: 'off/%s' % x, fortunes)
    return set(fortunes)


@Command(['fortune', 'bofh', 'excuse'], ['name'])
def cmd(send, msg, args):
    """Returns a fortune.
    Syntax: !fortune <list|(-a|-o) (module)>
    """
    fortunes = get_list().union(get_list(True))
    if msg == 'list':
        send(" ".join(sorted(fortunes)))
    else:
        cmd = ['fortune', '-s']
        match = re.match('(-[ao])( .+|$)', msg)
        if match:
            cmd.append(match.group(1))
            msg = match.group(2).strip()
        if 'bofh' in args['name'] or 'excuse' in args['name']:
            if random() < 0.05:
                send("BOFH Excuse #1337:")
                send("You don't exist, go away!")
                return
            cmd.append('bofh-excuses')
        elif msg in fortunes:
            cmd.append(msg)
        elif msg:
            send("%s is not a valid fortune module" % msg)
            return
        output = subprocess.check_output(cmd).decode()
        for line in output.splitlines():
            send(line)
