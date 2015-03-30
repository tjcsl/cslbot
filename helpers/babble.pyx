# -*- coding: utf-8 -*-
# distutils: language=c++
# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi,
# Samuel Damashek, James Forcier, and Reed Koser
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
import collections
import string as pystring
from sqlalchemy import Index, or_
from helpers.orm import Log, Babble, Babble_last, Babble_count
from libcpp.map cimport map
from libcpp.pair cimport pair
from libcpp.string cimport string
from libcpp.vector cimport vector


def get_messages(cursor, cmdchar, ctrlchan, speaker, newer_than_id):
    query = cursor.query(Log).filter(Log.id > newer_than_id)
    # Ignore commands, and messages addressed to the ctrlchan
    query = query.filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), ~Log.msg.startswith(cmdchar), Log.target != ctrlchan)
    if speaker is not None:
        location = 'target' if speaker.startswith('#') else 'source'
        query = query.filter(getattr(Log, location).ilike(speaker, escape='$'))
    return query.order_by(Log.id).all()


exclude_re = re.compile('https?://|^[0-9%s]+$' % pystring.punctuation)


cdef vector[string] clean_msg(msg) except *:
    return [x.encode() for x in msg.split() if not exclude_re.match(x)]


cdef map[string, int] get_markov(cursor, vector[string] node, initial_run) except *:
    key, source, target = node[0].c_str(), node[1].c_str(), node[2].c_str()
    cdef map[string, int] ret
    if initial_run:
        return ret
    old = cursor.query(Babble).filter(Babble.key == key, Babble.source == source, Babble.target == target).all()
    for row in old:
        ret.insert(pair[string, int](row.word, row.freq))
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


ctypedef map[vector[string], map[string, int]] MarkovDict

cdef MarkovDict generate_markov(cursor, messages, curr, cmdchar, ctrlchan, speaker, lastrow, initial_run) except *:
    cdef MarkovDict markov
    cdef vector[string] node
    for row in messages:
        msg = clean_msg(row.msg)
        for i in range(2,len(msg)):
            #FIXME: use c strings
            prev = msg[i-2] + " ".encode() + msg[i-1]
            node = <vector[string]>[prev, row.source.encode(), row.target.encode()]
            if markov.find(node) == markov.end():
                markov[node] = get_markov(cursor, node, initial_run)
            if markov[node][msg[i]]:
                markov[node][msg[i]] = markov[node][msg[i]] + 1
            else:
                markov[node][msg[i]] = 1
    return markov


cdef build_rows(cursor, MarkovDict markov, initial_run): #FIXME: except *
    data = []
    count_source = collections.defaultdict(int)
    count_target = collections.defaultdict(int)
    for pair in markov:
        node, word_freqs = pair.first, pair.second
        for freq_pair in word_freqs:
            word, freq = freq_pair.first, freq_pair.second
            row = None
            key, source, target = node
            if not initial_run:
                row = cursor.query(Babble).filter(Babble.key == key.c_str(), Babble.source == source.c_str(), Babble.target == target.c_str(), Babble.word == word.c_str()).first()
            if row:
                row.freq = freq
            else:
                if initial_run:
                    count_source[source] += 1
                    count_target[target] += 1
                else:
                    update_count(cursor, source, target)
                data.append({'source': source, 'target': target, 'key': key, 'word': word, 'freq': freq})
    count_data = []
    for source, count in count_source.items():
        count_data.append({'type': 'source', 'key': source, 'count': count})
    for target, count in count_target.items():
        count_data.append({'type': 'target', 'key': target, 'count': count})
    return data, count_data


def build_markov(cursor, cmdchar, ctrlchan, speaker=None, initial_run=False):
    """ Builds a markov dictionary."""
    if initial_run:
        cursor.query(Babble_last).delete()
    lastrow = cursor.query(Babble_last).first()
    if not lastrow:
        lastrow = Babble_last(last=0)
        cursor.add(lastrow)
    messages = get_messages(cursor, cmdchar, ctrlchan, speaker, lastrow.last)
    # FIXME: count can be too low if speaker is not None
    curr = messages[-1].id if messages else None
    markov = generate_markov(cursor, messages, curr, cmdchar, ctrlchan, speaker, lastrow, initial_run)
    # FIXME: cythonize data, count_data?
    data, count_data = build_rows(cursor, markov, initial_run)
    if initial_run:
        cursor.execute('DROP INDEX IF EXISTS ix_babble_key')
        cursor.execute(Babble.__table__.delete())
        cursor.execute(Babble_count.__table__.delete())
    cursor.bulk_insert_mappings(Babble, data)
    cursor.bulk_insert_mappings(Babble_count, count_data)
    if curr is not None:
        lastrow.last = curr
    if initial_run:
        key_index = Index('ix_babble_key', Babble.key)
        key_index.create(cursor.connection())
    cursor.commit()
