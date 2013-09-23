# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, Reed Koser, and James Forcier
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

args = ['db']


def build_markov(cursor, nick):
    """ Builds a markov dictionary of the form
        word : {
           nextword1 : num_apperences,
           nextword2 : num_apperances,
           ....
           nextwordn : num_apperances
        }
    """
    messages = cursor.execute("SELECT msg FROM log WHERE UPPER(source)=UPPER(?)", (nick,)).fetchall()
    markov = {}
    if messages is None or len(messages) == 0:
        return markov
    for msg in messages:
        msg = msg[0].split()
        for i in range(1, len(msg)):
            if msg[i - 1] not in markov:
                markov[msg[i - 1]] = {}
            if msg[i] not in markov[msg[i - 1]]:
                markov[msg[i - 1]][msg[i]] = 1
            else:
                markov[msg[i - 1]][msg[i]] += 1
    return markov


def build_msg(markov, nick):
    if len(markov.keys()) == 0:
        return "No one has talked with %s =(" % nick
    msg = choice(list(markov.keys()))
    last_word = msg
    while len(msg) < 100:
        if last_word not in markov.keys() or len(list(markov[last_word])) == 0:
            break
        next_word = choice(list(markov[last_word]))
        msg = "%s %s" % (msg, next_word)
        last_word = next_word
    return msg


def get_nick(cursor):
    rows = cursor.execute("SELECT source from log WHERE type='privmsg' OR type='pubmsg'").fetchall()
    nicks = list(set(row['source'].split('!')[0] for row in rows))
    return choice(nicks)


def cmd(send, msg, args):
    """Babbles like a user
    Syntax: !babble (nick)
    """
    cursor = args['db']
    if not msg:
        msg = get_nick(cursor)
        send(msg)
    markov = build_markov(cursor, msg.split()[0])
    send(build_msg(markov, msg))
