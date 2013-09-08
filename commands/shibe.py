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

from random import choice, randint

args = ['nick', 'modules']


def cmd(send, msg, args):
    """Generates a shibe reaction.
    Syntax: !shibe (topic1)...(topicn) or !shibe (number) for random words
    """
    topics = msg.split()
    reaction = 'wow'
    adverbs = ['so', 'such']
    if len(topics) == 1 && topics[0].isdigit():
        for i in range(int(topics[0])):
            reaction += ' %s &s' % (choice(adverbs, args['modules']['word'].gen_word())
    else:
        for i in topics:
            reaction += ' %s %s' % (choice(adverbs), i)

    quotes = ['omg', 'amaze', 'nice', 'clap', 'cool', 'doge', 'shibe']
    for i in range(randint(1, 2)):
        reaction += ' %s' % choice(quotes)
    reaction += ' wow'
    send(reaction)
