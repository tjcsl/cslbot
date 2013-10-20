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

from helpers.command import Command
from random import choice, random


@Command(['skasturi'])
def cmd(send, msg, args):
    """Gives a a random, non senscial issue.
    Syntax: !skasturi
    """
    a = ["add", "implement", "fix", "remove"]
    b = ["compressor", "engine", "lift", "elevator", "irc bot", "stabilizer",
         "computer", "ahamilto", "csl", "4506", "router", "switch", "thingy",
         "capacitor"]
    c = ["cslbot", "my room", "hooks", "nature", "the IMAX theater", "nowhere"]
    if random < .9:
        send("!issue %s %s in %s" % ((choice(a), choice(b), choice(c))))
    else:
        send("!issue skasturi makes too many issues")
