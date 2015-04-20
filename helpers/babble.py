# -*- coding: utf-8 -*-
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import re
import time
import collections
import string
from sqlalchemy import Index, or_
from sqlalchemy.exc import OperationalError
from helpers.orm import Log, Babble, Babble_last, Babble_count


def get_messages(cursor, cmdchar, ctrlchan, speaker, newer_than_id):
    query = cursor.query(Log).filter(Log.id > newer_than_id)
    # Ignore commands, and messages addressed to the ctrlchan
    query = query.filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), ~Log.msg.startswith(cmdchar), Log.target != ctrlchan)
    if speaker is not None:
        location = 'target' if speaker.startswith('#') else 'source'
        query = query.filter(getattr(Log, location).ilike(speaker, escape='$'))
    return query.order_by(Log.id).all()


exclude_re = re.compile('https?://|^[0-9%s]+$' % string.punctuation)


def clean_msg(msg):
    return [x for x in msg.split() if not exclude_re.match(x)]


def get_markov(cursor, node, initial_run):
    ret = collections.defaultdict(int)
    if initial_run:
        return ret
    key, source, target = node
    old = cursor.query(Babble).filter(Babble.key == key, Babble.source == source, Babble.target == target).all()
    ret.update({x.word: x.freq for x in old})
    return ret


def update_count(cursor, source, target):
    count_source = cursor.query(Babble_count).filter(Babble_count.type == 'source', Babble_count.key == source).first()
    if count_source:
        count_source.count = count_source.count + 1
    else:
        cursor.add(Babble_count(type='source', key=source, count=1))
    count_target = cursor.query(Babble_count).filter(Babble_count.type == 'target', Babble_count.key == target).first()
    if count_target:
        count_target.count = count_target.count + 1
    else:
        cursor.add(Babble_count(type='target', key=target, count=1))


def generate_markov(cursor, cmdchar, ctrlchan, speaker, lastrow, initial_run):
    markov = {}
    messages = get_messages(cursor, cmdchar, ctrlchan, speaker, lastrow.last)
    # FIXME: count can be too low if speaker is not None
    curr = messages[-1].id if messages else None
    for row in messages:
        msg = clean_msg(row.msg)
        for i in range(2, len(msg)):
            prev = "%s %s" % (msg[i - 2], msg[i - 1])
            node = (prev, row.source, row.target)
            if node not in markov:
                markov[node] = get_markov(cursor, node, initial_run)
            markov[node][msg[i]] += 1
    return curr, markov


def build_rows(cursor, markov, initial_run):
    data = []
    count_source = collections.defaultdict(int)
    count_target = collections.defaultdict(int)
    for node, word_freqs in markov.items():
        for word, freq in word_freqs.items():
            row = None
            key, source, target = node
            if not initial_run:
                row = cursor.query(Babble).filter(Babble.key == key, Babble.source == source, Babble.target == target, Babble.word == word).first()
            if row:
                row.freq = freq
            else:
                if initial_run:
                    count_source[source] += 1
                    count_target[target] += 1
                else:
                    update_count(cursor, source, target)
                data.append((source, target, key, word, freq))
    count_data = []
    for source, count in count_source.items():
        count_data.append({'type': 'source', 'key': source, 'count': count})
    for target, count in count_target.items():
        count_data.append({'type': 'target', 'key': target, 'count': count})
    return data, count_data


def build_markov(cursor, cmdchar, ctrlchan, speaker=None, initial_run=False, debug=False):
    """ Builds a markov dictionary."""
    if initial_run:
        cursor.query(Babble_last).delete()
    lastrow = cursor.query(Babble_last).first()
    if not lastrow:
        lastrow = Babble_last(last=0)
        cursor.add(lastrow)
    if debug:
        t = time.time()
    curr, markov = generate_markov(cursor, cmdchar, ctrlchan, speaker, lastrow, initial_run)
    if debug:
        print('Generated markov in %f' % (time.time() - t))
        t = time.time()
    data, count_data = build_rows(cursor, markov, initial_run)
    if debug:
        print('Rows built in %f' % (time.time() - t))
    if initial_run:
        if debug:
            t = time.time()
        cursor.execute('DROP INDEX IF EXISTS ix_babble_key')
        cursor.execute(Babble.__table__.delete())
        cursor.execute(Babble_count.__table__.delete())
        if debug:
            print('Created index in %f' % (time.time() - t))
    if debug:
        t = time.time()
    if initial_run and cursor.bind.dialect.name == 'postgresql':
        # Crazy magic to insert a ton of data really fast, drops runtime in half on large datasets.
        raw_cursor = cursor.connection().connection.cursor()
        prev = 0
        for i in range(20000, len(data), 20000):
            args_str = '\n'.join([raw_cursor.mogrify("INSERT INTO babble (source,target,key,word,freq) VALUES(%s,%s,%s,%s,%s);", x).decode() for x in data[prev:i]])
            # Don't die on empty log table.
            if args_str:
                raw_cursor.execute(args_str)
            prev = i
        args_str = '\n'.join([raw_cursor.mogrify("INSERT INTO babble (source,target,key,word,freq) VALUES(%s,%s,%s,%s,%s);", x).decode() for x in data[prev:]])
        # Don't die on empty log table.
        if args_str:
            raw_cursor.execute(args_str)
    else:
        data = [{'source': x[0], 'target': x[1], 'key': x[2], 'word': x[3], 'freq': x[4]} for x in data]
        cursor.bulk_insert_mappings(Babble, data)
    cursor.bulk_insert_mappings(Babble_count, count_data)
    if debug:
        print('Inserted rows in %f' % (time.time() - t))
    if curr is not None:
        lastrow.last = curr
    if initial_run:
        if debug:
            t = time.time()
        key_index = Index('ix_babble_key', Babble.key)
        key_index.create(cursor.connection())
        if debug:
            print('Created index in %f' % (time.time() - t))
    if debug:
        t = time.time()
    cursor.commit()
    if debug:
        print('Commited in %f' % (time.time() - t))


def update_markov(cursor, config):
    cmdchar = config['core']['cmdchar']
    ctrlchan = config['core']['ctrlchan']
    try:
        # FIXME: support locking for other dialects?
        if cursor.bind.dialect.name == 'postgresql':
            cursor.execute('LOCK TABLE babble IN EXCLUSIVE MODE NOWAIT')
            cursor.execute('LOCK TABLE babble_count IN EXCLUSIVE MODE NOWAIT')
            cursor.execute('LOCK TABLE babble_last IN EXCLUSIVE MODE NOWAIT')
        build_markov(cursor, cmdchar, ctrlchan)
        return True
    except OperationalError as ex:
        # If we can't lock the table, silently skip updating and wait for the next time we're called.
        if 'could not obtain lock on relation "babble' not in str(ex):
            raise
        return False
