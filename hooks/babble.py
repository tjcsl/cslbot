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

import collections
from sqlalchemy import or_
from helpers.hook import Hook
from helpers.orm import Log, Babble


def get_messages(cursor, speaker, cmdchar, ctrlchan):
    # Ignore all commands, messages addressed to people, and messages addressed to the ctrlchan
    query = cursor.query(Log).filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), ~Log.msg.startswith(cmdchar), ~Log.msg.like('%:%'),
                                     Log.target != ctrlchan)
    if speaker is not None:
        location = 'target' if speaker.startswith('#') else 'source'
        query = query.filter(getattr(Log, location).ilike(speaker, escape='$'))
    return query.all()

Node = collections.namedtuple('Node', ['freq', 'source', 'target'])


def build_markov(cursor, speaker, cmdchar, ctrlchan):
    """ Builds a markov dictionary."""
    markov = {}
    messages = get_messages(cursor, speaker, cmdchar, ctrlchan)
    for row in messages:
        msg = row.msg.split()
        for i in range(2, len(msg)):
            prev = "%s %s" % (msg[i-2], msg[i-1])
            if prev not in markov:
                markov[prev] = Node(collections.defaultdict(int), row.source, row.target)
            markov[prev].freq[msg[i]] += 1
    data = []
    for key, node in markov.items():
        for word, freq in node.freq.items():
            data.append({'source': node.source, 'target': node.target, 'key': key, 'word': word, 'freq': freq})
    # FIXME cursor.execute(Babble.__table__.delete())
    # FIXME cursor.bulk_insert_mappings(Babble, data)
    cursor.commit()


@Hook('babble', ['pubmsg', 'privmsg'], ['db', 'source', 'target'])
def hook(send, msg, args):
    # No babble cache, nothing to update
    if not args['db'].query(Babble).count():
        return
    # FIXME: make this do something
