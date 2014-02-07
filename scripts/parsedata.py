#!/usr/bin/python3 -OO
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from time import strftime
from datetime import datetime
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader
from os.path import dirname, exists
from os import mkdir
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


#FIXME: don't duplicate helpers/sql.py
def get_session(config):
    #FIXME: add support for sqlite connection string
    engine = create_engine('postgresql://ircbot:%s@localhost/%s' % (config['auth']['dbpass'], config['core']['dbname']))
    return Session(bind=engine)


def get_quotes(cursor):
    rows = cursor.execute('SELECT id,quote,nick,submitter FROM quotes WHERE approved=1').fetchall()
    return [dict(row) for row in rows]


def get_scores(cursor):
    rows = cursor.execute('SELECT nick,score FROM scores').fetchall()
    return [dict(row) for row in rows]


def get_urls(cursor):
    rows = cursor.execute('SELECT url,title,time FROM urls ORDER BY time DESC').fetchall()
    urls = []
    for row in rows:
        urls.append({'time': datetime.fromtimestamp(row['time']), 'title': row['title'], 'url': row['url']})
    return urls


def get_polls(cursor):
    rows = cursor.execute('SELECT id,question FROM polls WHERE deleted=0 AND active=1 ORDER BY id').fetchall()
    polls = OrderedDict()
    for row in rows:
        polls[row['id']] = row['question']
    return polls


def get_responses(cursor, polls):
    responses = {}
    for id in polls.keys():
        responses[id] = {}
        rows = cursor.execute('SELECT response,voter FROM poll_responses WHERE id=%s', (id,)).fetchall()
        for row in rows:
            if row['response'] not in responses[id]:
                responses[id][row['response']] = []
            responses[id][row['response']].append(row['voter'])
    return responses


def get_winners(polls, responses):
    winners = {}
    for id in polls.keys():
        ranking = {}
        for response, voters in responses[id].items():
            num = len(voters)
            if num not in ranking:
                ranking[num] = []
            ranking[num].append(response)
        if ranking:
            high = max(ranking)
            if len(ranking[high]) == 1:
                winners[id] = "The winner is %s with %d votes." % (ranking[high][0], high)
            else:
                winners[id] = "Tie between %s with %d votes." % (", ".join(ranking[high]), high)
        else:
            winners[id] = ""
    return winners


def output_quotes(env, cursor, outdir, time):
    args = {'quotes': get_quotes(cursor), 'time': time}
    output = env.get_template('quotes.html').render(**args)
    open(outdir + '/quotes.html', 'w', encoding='utf8').write(output)


def output_scores(env, cursor, outdir, time):
    args = {'scores': get_scores(cursor), 'time': time}
    output = env.get_template('scores.html').render(**args)
    open(outdir + '/scores.html', 'w', encoding='utf8').write(output)


def output_polls(env, cursor, outdir, time):
    polls = get_polls(cursor)
    responses = get_responses(cursor, polls)
    args = {'polls': polls, 'responses': responses, 'winners': get_winners(polls, responses), 'time': time}
    output = env.get_template('polls.html').render(**args)
    open(outdir + '/polls.html', 'w', encoding='utf8').write(output)


def output_urls(env, cursor, outdir, time):
    urls = get_urls(cursor)
    args = {'urls': urls, 'time': time}
    output = env.get_template('urls.html').render(**args)
    open(outdir + '/urls.html', 'w', encoding='utf8').write(output)


def main(config, outdir):
    cursor = get_session(config).connection()
    env = Environment(loader=FileSystemLoader(dirname(__file__)+'/../static/templates'))
    time = strftime('Last Updated at %I:%M %p on %a, %b %d, %Y')

    if not exists(outdir):
        mkdir(outdir)

    output_quotes(env, cursor, outdir, time)
    output_scores(env, cursor, outdir, time)
    output_polls(env, cursor, outdir, time)
    output_urls(env, cursor, outdir, time)


if __name__ == '__main__':
    config = ConfigParser()
    config.read_file(open(dirname(__file__) + '/../config.cfg'))
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='The output dir.')
    args = parser.parse_args()
    main(config, args.output)
