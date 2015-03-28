import re
import collections
from sqlalchemy import or_
from helpers.orm import Log, Babble, Babble_last, Babble_count

MarkovKey = collections.namedtuple('MarkovKey', ['key', 'source', 'target'])


def get_messages(cursor, cmdchar, ctrlchan, speaker=None, newer_than_id=0):
    query = cursor.query(Log).filter(Log.id > newer_than_id)
    # Ignore commands, and messages addressed to the ctrlchan
    query = query.filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), ~Log.msg.startswith(cmdchar), Log.target != ctrlchan)
    if speaker is not None:
        location = 'target' if speaker.startswith('#') else 'source'
        query = query.filter(getattr(Log, location).ilike(speaker, escape='$'))
    return query.order_by(Log.id).all()


def clean_msg(msg):
    return [x for x in msg.split() if not re.match('https?://', x)]


def get_markov(cursor, node):
    ret = collections.defaultdict(int)
    old = cursor.query(Babble).filter(Babble.key == node.key, Babble.source == node.source, Babble.target == node.target).all()
    ret.update({x.word: x.freq for x in old})
    return ret


def build_markov(cursor, cmdchar, ctrlchan, speaker=None):
    """ Builds a markov dictionary."""
    markov = {}
    lastrow = cursor.query(Babble_last).first()
    if not lastrow:
        lastrow = Babble_last(last=0)
        cursor.add(lastrow)
    messages = get_messages(cursor, cmdchar, ctrlchan, speaker, newer_than_id=lastrow.last)
    if not messages:
        return
    curr = messages[-1].id
    for row in messages:
        msg = clean_msg(row.msg)
        for i in range(2, len(msg)):
            prev = "%s %s" % (msg[i - 2], msg[i - 1])
            node = MarkovKey(prev, row.source, row.target)
            if node not in markov:
                markov[node] = get_markov(cursor, node)
            markov[node][msg[i]] += 1
    data = []
    count_source = collections.defaultdict(int)
    count_target = collections.defaultdict(int)
    for node, word_freqs in markov.items():
        for word, freq in word_freqs.items():
            row = cursor.query(Babble).filter(Babble.key == node.key, Babble.source == node.source, Babble.target == node.target, Babble.word == word).first()
            if row:
                row.freq = freq
            else:
                count_source[node.source] += 1
                count_target[node.target] += 1
                data.append({'source': node.source, 'target': node.target, 'key': node.key, 'word': word, 'freq': freq})
    count_objects = []
    for source, count in count_source.items():
        count_objects.append(Babble_count(type='source', key=source, count=count))
    for target, count in count_target.items():
        count_objects.append(Babble_count(type='target', key=target, count=count))
    cursor.bulk_insert_mappings(Babble, data)
    cursor.bulk_save_objects(count_objects)
    lastrow.last = curr
    cursor.commit()
