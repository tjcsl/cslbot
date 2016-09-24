#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett,
# and Fox Wilson
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
import configparser
import fcntl
import shutil
import sys
from datetime import datetime, timedelta
from os import makedirs, path
from time import strftime
from typing import Any

from jinja2 import Environment, FileSystemLoader

from pkg_resources import Requirement, resource_filename
from sqlalchemy.orm import Session

# Make this work from git.
if path.exists(path.join(path.dirname(__file__), '..', '.git')):
    sys.path.insert(0, path.join(path.dirname(__file__), '..'))

from cslbot.helpers.orm import (Poll_responses,  # noqa
                                Polls,
                                Quotes,
                                Scores,
                                Urls)
from cslbot.helpers.sql import get_session  # noqa


def get_quotes(session: Session) -> List[Quotes]:
    return session.query(Quotes).filter(Quotes.accepted == 1).order_by(Quotes.id).all()


def get_scores(session: Session) -> List[Scores]:
    return session.query(Scores).order_by(Scores.score.desc()).all()


def get_urls(session: Session) -> List[Dict[str, Any]]:
    # FIXME: support stuff older than one week
    limit = datetime.now() - timedelta(weeks=1)
    rows = session.query(Urls).filter(Urls.time > limit).order_by(Urls.time.desc()).all()
    urls = []
    for row in rows:
        urls.append({'time': row.time, 'title': row.title, 'url': row.url})
    return urls


def get_polls(session: Session) -> Dict[int, str]:
    rows = session.query(Polls).filter(Polls.deleted == 0, Polls.active == 1).order_by(Polls.id).all()
    polls = collections.OrderedDict()  # type: Dict[int, str]
    for row in rows:
        polls[row.id] = row.question
    return polls


def get_responses(session: Session, polls: Dict[int, str]) -> Dict[int, Dict[str, List[str]]]:
    responses = {}  # type: Dict[int, Dict[str, List[str]]]
    for pid in polls.keys():
        responses[pid] = collections.OrderedDict()
        rows = session.query(Poll_responses).filter(Poll_responses.pid == pid).order_by(Poll_responses.response).all()
        for row in rows:
            responses[pid].setdefault(row.response, []).append(row.voter)
    return responses


def get_winners(polls: Dict[int, str], responses: Dict[int, Dict[str, List[str]]]) -> Dict[int, str]:
    winners = {}
    for pid in polls.keys():
        ranking = collections.defaultdict(list)  # type: Dict[int, List[str]]
        for response, voters in responses[pid].items():
            num = len(voters)
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


def output_quotes(env: Environment, session: Session, outdir: str, time: str) -> None:
    args = {'quotes': get_quotes(session), 'time': time}
    output = env.get_template('quotes.html').render(**args)
    with open('%s/quotes.html' % outdir, 'w', encoding='utf8') as f:
        f.write(output)


def output_scores(env: Environment, session: Session, outdir: str, time: str) -> None:
    args = {'scores': get_scores(session), 'time': time}
    output = env.get_template('scores.html').render(**args)
    with open('%s/scores.html' % outdir, 'w', encoding='utf8') as f:
        f.write(output)


def output_polls(env: Environment, session: Session, outdir: str, time: str) -> None:
    polls = get_polls(session)
    responses = get_responses(session, polls)
    args = {'polls': polls, 'responses': responses, 'winners': get_winners(polls, responses), 'time': time}
    output = env.get_template('polls.html').render(**args)
    with open('%s/polls.html' % outdir, 'w', encoding='utf8') as f:
        f.write(output)


def output_urls(env: Environment, session: Session, outdir: str, time: str):
    urls = get_urls(session)
    args = {'urls': urls, 'time': time}
    output = env.get_template('urls.html').render(**args)
    with open('%s/urls.html' % outdir, 'w', encoding='utf8') as f:
        f.write(output)


def main(confdir: str = "/etc/cslbot") -> None:
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(path.join(confdir, 'config.cfg')) as f:
        config.read_file(f)
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir', help='The output dir.')
    cmdargs = parser.parse_args()
    session = get_session(config)()
    template_path = resource_filename(Requirement.parse('CslBot'), 'cslbot/templates')
    env = Environment(loader=FileSystemLoader(template_path))
    time = strftime('Last Updated at %I:%M %p on %a, %b %d, %Y')

    if not path.exists(cmdargs.outdir):
        makedirs(cmdargs.outdir)
    lockfile = open(path.join(cmdargs.outdir, '.lock'), 'w')
    fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # Copy the js
    shutil.copy(path.join(template_path, 'sorttable.js'), cmdargs.outdir)

    output_quotes(env, session, cmdargs.outdir, time)
    output_scores(env, session, cmdargs.outdir, time)
    output_polls(env, session, cmdargs.outdir, time)
    output_urls(env, session, cmdargs.outdir, time)

    fcntl.lockf(lockfile, fcntl.LOCK_UN)
    lockfile.close()


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    main(path.join(path.dirname(__file__), '..'))
