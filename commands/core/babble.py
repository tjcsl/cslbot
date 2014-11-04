# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, Reed Koser, and James Forcier
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
from collections import namedtuple
from threading import Lock
from random import choice
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from helpers.command import Command
from helpers.orm import Log

MarkovState = namedtuple('MarkovState', ['time', 'data'])

# Keep cached results for five minutes
CACHE_LIFE = 60 * 5

# FIXME: have a better caching mechanism.
markov_map = {}
markov_lock = Lock()


# Make the generated messages look better.
def clean_msg(msg):
    msg = msg.replace('"', '')
    msg = [x for x in msg.split() if not re.match('https?://', x)]
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
    return choice(l)


def get_messages(cursor, speaker, cmdchar, ctrlchan):
    location = 'target' if speaker.startswith('#') else 'source'
    # FIXME: is python random sort faster?
    return cursor.query(Log.msg).filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), getattr(Log, location).ilike(speaker, escape='$'),
                                        ~Log.msg.startswith(cmdchar), ~Log.msg.like('%:%'), Log.target != ctrlchan).order_by(func.random()).all()


# FIXME: make sphinx happy
def build_markov(cursor, speaker, cmdchar, ctrlchan):
    """ Builds a markov dictionary of the form

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


def get_markov(cursor, speaker, defer, cmdchar, ctrlchan):
    if speaker not in markov_map:
        update_markov(cursor, speaker, cmdchar, ctrlchan)
    else:
        with markov_lock:
            if time.time() - markov_map[speaker].time > CACHE_LIFE:
                defer(0, update_markov, cursor, speaker, cmdchar, ctrlchan)
    with markov_lock:
        markov = markov_map[speaker].data
    return markov


def update_markov(cursor, speaker, cmdchar, ctrlchan):
    data = build_markov(cursor, speaker, cmdchar, ctrlchan)
    with markov_lock:
        markov_map[speaker] = MarkovState(time.time(), data)


def build_msg(markov, speaker):
    if len(markov.keys()) == 0:
        return "%s hasn't said anything =(" % speaker
    msg = choice(list(markov.keys()))
    last_word = msg
    while len(msg) < 100:
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
    markov = get_markov(args['db'], speaker, args['handler'].workers.defer, corecfg['cmdchar'], corecfg['ctrlchan'])
    send(build_msg(markov, speaker))
