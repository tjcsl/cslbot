# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, Reed Koser, and James Forcier
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import re
from random import choice, randint
from helpers.command import Command

#We need to know what can end a sentence
_sentence_ends = ".!?"


# Make the generated messages look better.
def clean_msg(msg):
    msg = msg.replace('"', '')
    msg = [x for x in msg.split() if not re.match('https?://', x)]
    msg = [x.strip() for x in msg]
    return msg


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
    print("Choosing from", l)
    return choice(l)


def get_messages(cursor, speaker, cmdchar):
    location = 'target' if speaker.startswith('#') else 'source'
    query = "SELECT msg FROM log WHERE type='pubmsg' AND UPPER(%s)=UPPER(?) AND msg NOT LIKE '%s%%' AND msg NOT LIKE'%%:%%' ORDER BY RANDOM()" % (location, cmdchar)
    return cursor.execute(query, (speaker,)).fetchall()


def update_freq_map(prefix, suffix, m):
    if prefix not in m:
        m[prefix] = {}
    if suffix not in m[prefix]:
        m[prefix][suffix] = 1
    else:
        m[prefix][suffix] += 1


#FIXME: make sphinx happy
def analyze_chat(messages, speaker):
    """ Builds a markov dictionary of the form

        word_list : {
           nextword1 : num_apperences,
           nextword2 : num_apperances,
           ....
           nextwordn : num_apperances
        }
    """
    markov = {}
    starts = {}
    ends = {}
    if messages is None or len(messages) == 0:
        return markov
    for msg in messages:
        msg = clean_msg(msg['msg'])
        #Make sure it's a real message
        if len(msg) == 0:
            continue
        if len(msg) < 4:
            continue
        print(msg)
        start = True
        while len(msg) > 2:
            prefix = msg[0:2]
            prefix_str = " ".join(prefix)
            suffix = msg[2]
            if start:
                update_freq_map(prefix_str, suffix, starts)
                start = False
            elif suffix[-1] in _sentence_ends:
                update_freq_map(prefix_str, suffix, ends)
            update_freq_map(prefix_str, suffix, markov)
            msg = msg[1:]
    return (starts, ends, markov)


def build_msg(markov, starts, ends, speaker):
    if len(markov.keys()) == 0:
        return "No one has talked with %s =(" % speaker
    count = 0
    mwords = randint(7, 20)
    prefix = choice(list(starts.keys()))
    suffix = weighted_rand(markov[prefix])
    out = str(prefix)  # Copy prefix
    print("Outputting")
    while count < mwords:
        print("out       ", out)
        if count > mwords - 4 and suffix[-1] in _sentence_ends:
            break

        if count > mwords - 4 and suffix[-1] == ',':
            mwords = count + 6

        if count > mwords - 3 and suffix[-1] not in _sentence_ends:
            mwords += 1

        print("suffix    ", suffix)
        if suffix is not None:
            out = out + " " + suffix
        prefix = " ".join(out.split()[-2:])
        #Clearly, we have reached the end of what we can do
        if prefix not in markov:
            break
        print("prefix    ", prefix)
        suffix = weighted_rand(markov[prefix])
        count += 1
    return speaker + " says: " + out


@Command('babble', ['db', 'config'])
def cmd(send, msg, args):
    """Babbles like a user
    Syntax: !babble (nick)
    """
    cursor = args['db']
    speaker = msg.split()[0] if msg else args['config']['core']['channel']
    messages = get_messages(cursor, speaker, args['config']['core']['cmdchar'])
    starts, ends, markov = analyze_chat(messages, speaker)
    send(build_msg(markov, starts, ends, speaker))
