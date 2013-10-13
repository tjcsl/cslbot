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

from random import choice, randint
from helpers.command import Command
from helpers.textutils import gen_word


@Command('shibe')
def cmd(send, msg, args):
    """Generates a shibe reaction.
    Syntax: !shibe (topic1)...(topicn)
    """
    topics = msg.split() if msg else [gen_word()]

    reaction = 'wow'
    adverbs = ['so', 'such', 'very', 'much', 'many']
    for i in topics:
        reaction += ' %s %s' % (choice(adverbs), i)

    quotes = ['omg', 'amaze', 'nice', 'clap', 'cool', 'doge', 'shibe', 'ooh']
    for i in range(randint(1, 2)):
        reaction += ' %s' % choice(quotes)
    reaction += ' wow'
    send(reaction)
