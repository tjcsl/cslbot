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

from random import choice
args = ['channels', 'target', 'config']


def cmd(send, msg, args):
    """Slap somebody.
    Syntax: !slap <nick> for <reason>
    """
    implements = ['a large trout', 'a clue-by-four', 'a fresh haddock', 'moon', 'an Itanium', 'fwilson', 'a wombat']
    slap = 'slaps %s around a bit with %s'
    if not msg:
        channel = args['target'] if args['target'] != 'private' else args['config']['core']['channel']
        users = list(args['channels'][channel].users())
        send(slap % (choice(users), choice(implements)), 'action')
    else:
        if "for" in msg:
            msg = msg.split("for")
            slap = slap % (msg[0].strip(), choice(implements) + " for" + msg[1])
        else:
            slap = slap % (msg, choice(implements))
        send(slap, 'action')
