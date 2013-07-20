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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import re
args = ['logs', 'target']


def cmd(send, msg, args):
    log = args['logs'][args['target']][:-1]
    if not msg:
        send(re.search(r"<.*> (.*)", log[-1][1]).groups(1)[0].strip()[::-1])
        return
    if re.search("^--", msg):
        user = msg[2:]
        for line in reversed(log[-50:]):
            if re.search(r"<@?\+?" + user + ">", line[1]):
                send(
                    re.search(r"<.*> (.*)", line[1]).groups(1)[0].strip()[::-1])
                return
        send("Couldn't find a message from " + user + " :(")
        return
    send(msg[::-1].strip())
