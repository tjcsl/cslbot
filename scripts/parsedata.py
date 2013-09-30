#!/usr/bin/python3 -OO
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import sqlite3
import argparse
from time import strftime
from jinja2 import Environment, FileSystemLoader
from os.path import dirname


def get_quotes(cursor):
    rows = cursor.execute('SELECT id,quote,nick FROM quotes').fetchall()
    return [list(row) for row in rows]


def output_quotes(env, cursor, outdir, time):
    quotes = get_quotes(cursor)
    output = env.get_template('quotes.html').render(quotes=quotes, time=time)
    open(outdir + '/quotes.html', 'w', encoding='utf8').write(output)


def get_scores(cursor):
    rows = cursor.execute('SELECT nick,score FROM scores').fetchall()
    return [list(row) for row in rows]


def output_scores(env, cursor, outdir, time):
    scores = get_scores(cursor)
    output = env.get_template('scores.html').render(scores=scores, time=time)
    open(outdir + '/scores.html', 'w', encoding='utf8').write(output)


def get_polls(cursor):
    rows = cursor.execute('SELECT pid,question FROM polls WHERE deleted=0 AND active=1').fetchall()
    return {row['pid']: row['question'] for row in rows}


def get_responses(cursor, polls):
    responses = {}
    for pid in polls.keys():
        responses[pid] = {}
        rows = cursor.execute('SELECT response,voter FROM poll_responses WHERE pid=?', (pid,)).fetchall()
        for row in rows:
            if row['response'] not in responses[pid]:
                responses[pid][row['response']] = []
            responses[pid][row['response']].append(row['voter'])
    return responses


def output_polls(env, cursor, outdir, time):
    polls = get_polls(cursor)
    responses = get_responses(cursor, polls)
    output = env.get_template('polls.html').render(polls=polls, responses=responses, time=time)
    open(outdir + '/polls.html', 'w', encoding='utf8').write(output)


def main(outdir):
    filename = dirname(__file__) + "/../db.sqlite"
    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    env = Environment(loader=FileSystemLoader(dirname(__file__)+'/../static/templates'))
    time = strftime('Last Updated at %I:%M %p on %a, %b %d, %Y')

    output_quotes(env, cursor, outdir, time)
    output_scores(env, cursor, outdir, time)
    output_polls(env, cursor, outdir, time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='The output dir.')
    args = parser.parse_args()
    main(args.output)
