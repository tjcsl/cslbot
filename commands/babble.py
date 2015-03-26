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
import bisect
import collections
import random
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from helpers.command import Command
from helpers.orm import Log, Babble, Babble_data

# Keep cached results for thirty minutes
CACHE_LIFE = 60 * 30


def weighted_next(data):
    tags, partialSums = [], []

    current_sum = 0

    for d in data:
        current_sum += d.freq
        partialSums.append(current_sum)
        tags.append(d.word)

    x = random.random() * partialSums[-1]
    return tags[bisect.bisect_right(partialSums, x)]


def get_messages(cursor, speaker, cmdchar, ctrlchan):
    # FIXME: don't dual store for nick/channel
    location = 'target' if speaker.startswith('#') else 'source'
    return cursor.query(Log.msg).filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), getattr(Log, location).ilike(speaker, escape='$'),
                                        ~Log.msg.startswith(cmdchar), ~Log.msg.like('%:%'), Log.target != ctrlchan).all()


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
    for msg in messages:
        msg = msg.msg.split()
        for i in range(2, len(msg)):
            prev = "%s %s" % (msg[i-2], msg[i-1])
            if prev not in markov:
                markov[prev] = collections.defaultdict(int)
            markov[prev][msg[i]] += 1
    data = []
    for key, values in markov.items():
        for word, freq in values.items():
            data.append({'nick': speaker, 'key': key, 'word': word, 'freq': freq})
    cursor.execute(Babble_data.__table__.insert().values(data))


def ensure_markov(cursor, speaker, handler, cmdchar, ctrlchan):
    # FIXME: use incremental updates
    markov = cursor.query(Babble).filter(Babble.nick == speaker).first()
    if not markov:
        update_markov(handler, speaker, cmdchar, ctrlchan)
    elif time.time() - markov.time > CACHE_LIFE and False:  # FIXME: updates nuke the cache first
        handler.workers.defer(0, False, update_markov, handler, speaker, cmdchar, ctrlchan)


def update_markov(handler, speaker, cmdchar, ctrlchan):
    with handler.db.session_scope() as cursor:
        # FIXME: update cache non-distructively
        cursor.query(Babble_data).filter(Babble_data.nick == speaker).delete()
        build_markov(cursor, speaker, cmdchar, ctrlchan)
        # FIXME: kill the babble table w/ incremental updates
        markov = cursor.query(Babble).filter(Babble.nick == speaker).first()
        if markov:
            markov.time = time.time()
        else:
            cursor.add(Babble(nick=speaker, time=time.time()))


def build_msg(cursor, speaker, start):
    markov = cursor.query(Babble_data).filter(Babble_data.nick == speaker).order_by(func.random()).first()
    if markov is None:
        return "%s hasn't said anything =(" % speaker
    if start is None:
        prev = markov.key
    else:
        # FIXME: make this faster
        markov = cursor.query(Babble_data).filter(Babble_data.nick == speaker, Babble_data.key.ilike(start+' %')).order_by(func.random()).first()
        if markov:
            prev = markov.key
        else:
            return "%s hasn't said %s" % (speaker, start)
    msg = prev
    while len(msg) < 256:
        # FIXME: investigate alt indicies
        data = cursor.query(Babble_data).filter(Babble_data.key == prev, Babble_data.nick == speaker).all()
        if not data:
            break
        next_word = weighted_next(data)
        msg = "%s %s" % (msg, next_word)
        prev = "%s %s" % (prev.split()[1], next_word)
    return "%s says: %s" % (speaker, msg)


@Command('babble', ['db', 'config', 'handler'])
def cmd(send, msg, args):
    """Babbles like a user
    Syntax: !babble (--start <word>) (nick)
    """
    corecfg = args['config']['core']
    match = re.match('--start (.+) (.+)', msg)
    start = None
    if match:
        start = match.group(1)
        speaker = match.group(2)
    elif msg:
        match = re.match('--start (.+)', msg)
        if match:
            start = match.group(1)
            speaker = corecfg['channel']
        else:
            speaker = msg.split()[0]
    else:
        speaker = corecfg['channel']
    ensure_markov(args['db'], speaker, args['handler'], corecfg['cmdchar'], corecfg['ctrlchan'])
    send(build_msg(args['db'], speaker, start))
