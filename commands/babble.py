# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, Reed Koser, and James Forcier
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

import re
import time
import itertools
import bisect
import collections
import random
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from helpers.command import Command
from helpers.orm import Log, Babble

# Keep cached results for thirty minutes
CACHE_LIFE = 60 * 30


# Make the generated messages look better.
def clean_msg(msg):
    msg = msg.replace('"', '')
    msg = [x for x in msg.split() if not re.match('https?://', x)]
    return msg


def weighted_rand(d):
    """ Gets a random key from d taking weights into account.

        d should be a dictionary of the form:
            {
                thing1: freq1,
                thing2: freq2,
                ...
                thingn: freqn
                }
    """
    l = collections.defaultdict(int)
    for k in d:
        l[k] += 1
    # from https://docs.python.org/3/library/random.html
    dist = list(itertools.accumulate(l.values()))
    x = random.random() * dist[-1]
    return list(l.keys())[bisect.bisect(dist, x)]


def get_messages(cursor, speaker, cmdchar, ctrlchan):
    location = 'target' if speaker.startswith('#') else 'source'
    return cursor.query(Log.msg).filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), getattr(Log, location).ilike(speaker, escape='$'),
                                        ~Log.msg.startswith(cmdchar), ~Log.msg.like('%:%'), Log.target != ctrlchan).order_by(func.random()).all()


def build_markov(cursor, speaker, cmdchar, ctrlchan):
    """ Builds a markov dictionary.

        Dictionary should be in the form:
            word : {
               nextword1 : num_apperences,
               nextword2 : num_apperances,
               ....
               nextwordn : num_apperances
               }
    """
    markov = {}
    messages = get_messages(cursor, speaker, cmdchar, ctrlchan)
    if messages is None or len(messages) == 0:
        return markov
    for msg in messages:
        msg = clean_msg(msg.msg)
        for i in range(1, len(msg)):
            if msg[i - 1] not in markov:
                markov[msg[i - 1]] = {}
            if msg[i] not in markov[msg[i - 1]]:
                markov[msg[i - 1]][msg[i]] = 1
            else:
                markov[msg[i - 1]][msg[i]] += 1
    return markov


def get_markov(cursor, speaker, handler, cmdchar, ctrlchan):
    markov = cursor.query(Babble).filter(Babble.nick == speaker).first()
    if not markov:
        update_markov(handler, speaker, cmdchar, ctrlchan)
        markov = cursor.query(Babble).filter(Babble.nick == speaker).first()
    elif time.time() - markov.time > CACHE_LIFE:
        handler.workers.defer(0, False, update_markov, handler, speaker, cmdchar, ctrlchan)
    return markov.data


def update_markov(handler, speaker, cmdchar, ctrlchan):
    with handler.db.session_scope() as cursor:
        data = build_markov(cursor, speaker, cmdchar, ctrlchan)
        markov = cursor.query(Babble).filter(Babble.nick == speaker).first()
        if markov:
            markov.time = time.time()
            markov.data = data
        else:
            cursor.add(Babble(nick=speaker, time=time.time(), data=data))


def build_msg(markov, speaker):
    if len(markov.keys()) == 0:
        return "%s hasn't said anything =(" % speaker
    msg = random.choice(list(markov.keys()))
    last_word = msg
    while len(msg) < 256:
        if last_word not in markov.keys() or len(list(markov[last_word])) == 0:
            break
        next_word = weighted_rand(markov[last_word])
        msg = "%s %s" % (msg, next_word)
        last_word = next_word
    return "%s says: %s" % (speaker, msg)


@Command('babble', ['db', 'config', 'handler'])
def cmd(send, msg, args):
    """Babbles like a user
    Syntax: !babble (nick)
    """
    corecfg = args['config']['core']
    speaker = msg.split()[0] if msg else corecfg['channel']
    markov = get_markov(args['db'], speaker, args['handler'], corecfg['cmdchar'], corecfg['ctrlchan'])
    send(build_msg(markov, speaker))
