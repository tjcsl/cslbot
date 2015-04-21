# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import bisect
import random
from sqlalchemy.sql.expression import func
from helpers import arguments
from helpers.command import Command
from helpers.orm import Babble, Babble_count


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
    count = cursor.query(Babble_count.count).filter(Babble_count.type == location, Babble_count.key == speaker).scalar()
    if count is None:
        return "%s hasn't said anything =(" % speaker
    if start is None:
        prev = cursor.query(Babble.key).filter(getattr(Babble, location) == speaker).offset(random.random() * count).limit(1).scalar()
    else:
        # FIXME: use Babble_count?
        if len(start) == 1:
            markov = cursor.query(Babble.key).filter(Babble.key.like('%s %%' % start[0]))
        elif len(start) == 2:
            markov = cursor.query(Babble.key).filter(Babble.key == " ".join(start))
        else:
            return "Please specify either one or two words for --start"
        prev = markov.filter(getattr(Babble, location) == speaker).order_by(func.random()).limit(1).scalar()
        if prev is None:
            return "%s hasn't said %s" % (speaker, " ".join(start))
    msg = prev
    while len(msg) < 256:
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
    Syntax: {command} [nick] [--start <word>]
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('speaker', nargs='?', default=args['config']['core']['channel'])
    parser.add_argument('--start', nargs='*')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if args['db'].query(Babble).count():
        send(build_msg(args['db'], cmdargs.speaker, cmdargs.start))
    else:
        send("Please run ./scripts/gen_babble.py to initialize the babble cache")
