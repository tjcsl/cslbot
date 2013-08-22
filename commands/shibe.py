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

args = ['nick']


def cmd(send, msg, args):
    """Generates a shibe reaction.
    Syntax: !shibe <topic> or !shibe <topic1> <topic2>
    """
    topics = msg.split()
    if len(topics) == 1:

    quotes = ['omg', 'amaze', 'nice', 'clap', 'cool', 'doge', 'shibe']
    send('wow. so ' + topics[0] + ' such ' + topics[1] + ' ' + choice(quotes) ' wow')
