#!/usr/bin/python3 -O
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

import argparse
import collections
import re
from configparser import ConfigParser
from sqlalchemy import Index, or_
from os.path import dirname
from sys import path

# HACK: allow sibling imports
path.append(dirname(__file__) + '/..')

from helpers.orm import Log, Babble, Babble_last, Babble_count
from helpers.sql import get_session

Node = collections.namedtuple('Node', ['freq', 'source', 'target'])


def get_messages(cursor, speaker, cmdchar, ctrlchan):
    # Ignore all commands, messages addressed to people, and messages addressed to the ctrlchan
    query = cursor.query(Log).filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), ~Log.msg.startswith(cmdchar), Log.target != ctrlchan)
    if speaker is not None:
        location = 'target' if speaker.startswith('#') else 'source'
        query = query.filter(getattr(Log, location).ilike(speaker, escape='$'))
    return query.order_by(Log.id).all()


def clean_msg(msg):
    return [x for x in msg.split() if not re.match('https?://', x)]


def build_markov(cursor, speaker, cmdchar, ctrlchan):
    """ Builds a markov dictionary."""
    # Keep synchronized with hooks/babble.py
    markov = {}
    print('Generating markov.')
    messages = get_messages(cursor, speaker, cmdchar, ctrlchan)
    last = messages[-1].id
    for row in messages:
        msg = clean_msg(row.msg)
        for i in range(2, len(msg)):
            prev = "%s %s" % (msg[i-2], msg[i-1])
            if prev not in markov:
                markov[prev] = Node(collections.defaultdict(int), row.source, row.target)
            markov[prev].freq[msg[i]] += 1
    data = []
    count_source = collections.defaultdict(int)
    count_target = collections.defaultdict(int)
    for key, node in markov.items():
        for word, freq in node.freq.items():
            count_source[node.source] += 1
            count_target[node.target] += 1
            data.append({'source': node.source, 'target': node.target, 'key': key, 'word': word, 'freq': freq})
    count_data = []
    for source, count in count_source.items():
        count_data.append({'type': 'source', 'key': source, 'count': count})
    for target, count in count_target.items():
        count_data.append({'type': 'target', 'key': target, 'count': count})
    print('Clearing tables.')
    cursor.execute('DROP INDEX IF EXISTS ix_babble_key')
    cursor.execute(Babble.__table__.delete())
    cursor.execute(Babble_count.__table__.delete())
    print('Inserting data.')
    cursor.bulk_insert_mappings(Babble, data)
    cursor.bulk_insert_mappings(Babble_count, count_data)
    meta_row = cursor.query(Babble_last).first()
    if meta_row:
        meta_row.last = last
    else:
        cursor.add(Babble_last(last=last))
    print('Creating indices.')
    key_index = Index('ix_babble_key', Babble.key)
    key_index.create(cursor.connection())
    print('Committing.')
    cursor.commit()


def main(config, speaker):
    session = get_session(config)()
    cmdchar = config['core']['cmdchar']
    ctrlchan = config['core']['ctrlchan']
    # FIXME: try psycopg2cffi/pypy3
    build_markov(session, speaker, cmdchar, ctrlchan)


if __name__ == '__main__':
    config = ConfigParser()
    config.read_file(open(dirname(__file__) + '/../config.cfg'))
    parser = argparse.ArgumentParser()
    parser.add_argument('--nick', help='The nick to generate babble cache for (testing only).')
    args = parser.parse_args()
    main(config, args.nick)
