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

args = ['nick', 'modules']


def cmd(send, msg, args):
    """Generates a shibe reaction.
    Syntax: !shibe or !shibe topic1 topic2...
    Use !wow for a random word.
    """
    msg = 'wow '
    topics = msg.split()
    if topics:
        adverbs = ['so ', 'such ']
        for i in range(0, len(topics))
            if topics[i] == '!wow':
                msg += choice(adverbs) + args['modules']['word'].gen_word() + ' '
            else:
                msg += choice(adverbs) + topics[i] + ' '
    quotes = ['omg ', 'amaze ', 'nice ', 'clap ', 'cool ', 'doge ', 'shibe ']
    for i in range(randint(1, 2))
        msg += choice(quotes)
    msg += 'wow'
    send(msg)
