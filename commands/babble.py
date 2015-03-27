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
import bisect
import random
from sqlalchemy.sql.expression import func
from helpers.command import Command
from helpers.orm import Babble


def weighted_next(data):
    tags, partialSums = [], []
    current_sum = 0

    for d in data:
        current_sum += d.freq
        partialSums.append(current_sum)
        tags.append(d.word)

    x = random.random() * partialSums[-1]
    return tags[bisect.bisect_right(partialSums, x)]


def build_msg(cursor, speaker, start):
    location = 'target' if speaker.startswith('#') else 'source'
    count = cursor.query(Babble).filter(getattr(Babble, location) == speaker).count()
    markov = cursor.query(Babble).filter(getattr(Babble, location) == speaker).offset(random.random()*count).first()
    if markov is None:
        return "%s hasn't said anything =(" % speaker
    if start is None:
        prev = markov.key
    else:
        # FIXME: make this faster
        markov = cursor.query(Babble).filter(getattr(Babble, location) == speaker, Babble.key.ilike(start+' %')).order_by(func.random()).first()
        if markov:
            prev = markov.key
        else:
            return "%s hasn't said %s" % (speaker, start)
    msg = prev
    while len(msg) < 256:
        # FIXME: investigate alt indicies
        data = cursor.query(Babble).filter(Babble.key == prev, getattr(Babble, location) == speaker).all()
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
    if args['db'].query(Babble).count():
        send(build_msg(args['db'], speaker, start))
    else:
        send("Please run ./scripts/gen_babble.py to initialize the babble cache")
