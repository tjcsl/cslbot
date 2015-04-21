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

from random import choice, randint
from helpers.command import Command


@Command('coin')
def cmd(send, msg, _):
    """Flips a coin a number of times.
    Syntax: {command} [number]
    """
    coin = ['heads', 'tails']
    if not msg:
        send('The coin lands on... %s' % choice(coin))
    elif not msg.isdigit():
        send("Not A Valid Positive Integer.")
    else:
        msg = int(msg)
        if msg < 0:
            send("Negative Flipping requires the (optional) quantum coprocessor.")
            return
        headFlips = randint(0, msg)
        tailFlips = msg - headFlips
        send('The coins land on heads %g times and on tails %g times.' % (headFlips, tailFlips))
