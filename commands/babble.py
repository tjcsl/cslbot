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

args = ['db', 'config']


# Make the generated messages look better.
def clean_msg(msg):
    msg = msg.replace('"', '')
    return msg.split()


def weighted_rand(d):
    """ d should be a dictionary of the form
    {
        thing1: freq1,
        thing2: freq2,
        ...
        thingn: freqn
    }
    """
    l = []
    for k in d:
        l += [k] * d[k]
    return choice(l)


#FIXME: make sphinx happy
def build_markov(cursor, speaker):
    """ Builds a markov dictionary of the form

        word : {
           nextword1 : num_apperences,
           nextword2 : num_apperances,
           ....
           nextwordn : num_apperances
        }
    """
    if speaker.startswith('#'):
        messages = cursor.execute("SELECT msg FROM log WHERE UPPER(target)=UPPER(?)", (speaker,)).fetchall()
    else:
        messages = cursor.execute("SELECT msg FROM log WHERE UPPER(source)=UPPER(?)", (speaker,)).fetchall()
    markov = {}
    if messages is None or len(messages) == 0:
        return markov
    for msg in messages:
        msg = clean_msg(msg['msg'])
        for i in range(1, len(msg)):
            if msg[i - 1] not in markov:
                markov[msg[i - 1]] = {}
            if msg[i] not in markov[msg[i - 1]]:
                markov[msg[i - 1]][msg[i]] = 1
            else:
                markov[msg[i - 1]][msg[i]] += 1
    return markov


def build_msg(markov, speaker):
    if len(markov.keys()) == 0:
        return "No one has talked with %s =(" % speaker
    msg = choice(list(markov.keys()))
    last_word = msg
    while len(msg) < 100:
        if last_word not in markov.keys() or len(list(markov[last_word])) == 0:
            break
        next_word = weighted_rand(markov[last_word])
        msg = "%s %s" % (msg, next_word)
        last_word = next_word
    return "%s says: %s" % (speaker, msg)


def cmd(send, msg, args):
    """Babbles like a user
    Syntax: !babble (nick)
    """
    cursor = args['db']
    speaker = msg.split()[0] if msg else args['config']['core']['channel']
    markov = build_markov(cursor, speaker)
    send(build_msg(markov, speaker))
