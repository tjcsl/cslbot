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
from random import getrandbits, randrange
from helpers.command import Command


@Command('random')
def cmd(send, msg, args):
    """For when you don't have enough randomness in your life.
    Syntax: !random (--int) (len)
    """
    match = re.match(r'--(.+?)\b', msg)
    randtype = 'hex'
    if match:
        if match.group(1) == 'int':
            randtype = 'int'
        else:
            send("Invalid Flag.")
            return
    if randtype == 'hex':
        send(hex(getrandbits(50)))
    else:
        maxlen = 1000000000
        msg = msg.split()
        if len(msg) == 2:
            if msg[1].isdigit():
                maxlen = int(msg[1])
            else:
                send("Invalid Length")
                return
        send(str(randrange(maxlen)))
