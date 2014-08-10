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
from sys import path
from configparser import ConfigParser

# HACK: allow sibling imports
path.append(dirname(__file__) + '/..')

from helpers.orm import Scores, Quotes, Polls, Poll_responses, Urls
from helpers.sql import get_session


def get_quotes(session):
    return session.query(Quotes).filter(Quotes.approved == 1).order_by(Quotes.id).all()


def get_scores(session):
    return session.query(Scores).all()


def get_urls(session):
    rows = session.query(Urls).order_by(Urls.time.desc()).all()
    urls = []
    for row in rows:
        urls.append({'time': datetime.fromtimestamp(row.time), 'title': row.title, 'url': row.url})
    return urls


def get_polls(session):
    rows = session.query(Polls).filter(Polls.deleted == 0, Polls.active == 1).order_by(Polls.id).all()
    polls = OrderedDict()
    for row in rows:
        polls[row.id] = row.question
    return polls


def get_responses(session, polls):
    responses = {}
    for pid in polls.keys():
        responses[pid] = {}
        rows = session.query(Poll_responses).filter(Poll_responses.pid == pid).all()
        for row in rows:
            if row.response not in responses[pid]:
                responses[pid][row.response] = []
            responses[pid][row.response].append(row.voter)
    return responses


def get_winners(polls, responses):
    winners = {}
    for pid in polls.keys():
        ranking = {}
        for response, voters in responses[pid].items():
            num = len(voters)
            if num not in ranking:
                ranking[num] = []
            ranking[num].append(response)
        if ranking:
            high = max(ranking)
            if len(ranking[high]) == 1:
                winners[pid] = "The winner is %s with %d votes." % (ranking[high][0], high)
            else:
                winners[pid] = "Tie between %s with %d votes." % (", ".join(ranking[high]), high)
        else:
            winners[pid] = ""
    return winners


def output_quotes(env, session, outdir, time):
    args = {'quotes': get_quotes(session), 'time': time}
    output = env.get_template('quotes.html').render(**args)
    open(outdir + '/quotes.html', 'w', encoding='utf8').write(output)


def output_scores(env, session, outdir, time):
    args = {'scores': get_scores(session), 'time': time}
    output = env.get_template('scores.html').render(**args)
    open(outdir + '/scores.html', 'w', encoding='utf8').write(output)


def output_polls(env, session, outdir, time):
    polls = get_polls(session)
    responses = get_responses(session, polls)
    args = {'polls': polls, 'responses': responses, 'winners': get_winners(polls, responses), 'time': time}
    output = env.get_template('polls.html').render(**args)
    open(outdir + '/polls.html', 'w', encoding='utf8').write(output)


def output_urls(env, session, outdir, time):
    urls = get_urls(session)
    args = {'urls': urls, 'time': time}
    output = env.get_template('urls.html').render(**args)
    open(outdir + '/urls.html', 'w', encoding='utf8').write(output)


def main(config, outdir):
    session = get_session(config)
    env = Environment(loader=FileSystemLoader(dirname(__file__)+'/../static/templates'))
    time = strftime('Last Updated at %I:%M %p on %a, %b %d, %Y')

    if not exists(outdir):
        mkdir(outdir)

    output_quotes(env, session, outdir, time)
    output_scores(env, session, outdir, time)
    output_polls(env, session, outdir, time)
    output_urls(env, session, outdir, time)


if __name__ == '__main__':
    config = ConfigParser()
    config.read_file(open(dirname(__file__) + '/../config.cfg'))
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='The output dir.')
    args = parser.parse_args()
    main(config, args.output)
