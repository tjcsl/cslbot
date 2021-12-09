# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.misc import escape
from ..helpers.orm import Babble, Babble2, Babble_count


def weighted_next(data):
    tags, partialSums = [], []
    current_sum = 0

    for d in data:
        current_sum += d.freq
        partialSums.append(current_sum)
        tags.append(d.word)

    x = random.random() * partialSums[-1]
    return tags[bisect.bisect_right(partialSums, x)]


def build_msg(cursor, speaker, length, start):
    table = Babble if length == 1 else Babble2
    location = 'target' if speaker.startswith(('#', '+', '@')) else 'source'
    # handle arguments that end in '\', which is valid in irc, but causes issues with sql.
    escaped_speaker = escape(speaker)
    count = cursor.query(Babble_count.count).filter(Babble_count.type == location, Babble_count.length == length,
                                                    Babble_count.key == escaped_speaker).scalar()
    if count is None:
        return "%s hasn't said anything =(" % speaker
    if start is None:
        prev = cursor.query(table.key).filter(getattr(table, location) == escaped_speaker).offset(random.random() * count).limit(1).scalar()
    else:
        # FIXME: use Babble_count?
        markov = cursor.query(table.key)
        if length == 2:
            if len(start) == 1:
                markov = markov.filter(table.key.like('%s %%' % escape(start[0])))
            elif len(start) == 2:
                markov = markov.filter(table.key == escape(" ".join(start)))
            else:
                return "Please specify either one or two words for --start"
        elif len(start) == 1:
            markov = markov.filter(table.key == escape(start[0]))
        else:
            return "Please specify one word for --start"
        prev = markov.filter(getattr(table, location) == escaped_speaker).order_by(func.random()).limit(1).scalar()
        if prev is None:
            return "{} hasn't said {}".format(speaker, " ".join(start))
    msg = prev
    while len(msg) < 400:
        data = cursor.query(table.freq, table.word).filter(table.key == prev, getattr(table, location) == escaped_speaker).all()
        if not data:
            break
        next_word = weighted_next(data)
        msg = f"{msg} {next_word}"
        if length == 2:
            prev = f"{prev.split()[1]} {next_word}"
        else:
            prev = next_word
    return f"{speaker} says: {msg}"


@Command('babble', ['db', 'config', 'handler'])
def cmd(send, msg, args):
    """Babbles like a user
    Syntax: {command} [nick] [--length <1|2>] [--start <word>]
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('speaker', nargs='?', default=args['config']['core']['channel'])
    parser.add_argument('--length', type=int, choices=[1, 2], default=2)
    parser.add_argument('--start', nargs='*')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if args['db'].query(Babble).count():
        send(build_msg(args['db'], cmdargs.speaker, cmdargs.length, cmdargs.start))
    else:
        send("Please run ./scripts/gen_babble.py to initialize the babble cache")
