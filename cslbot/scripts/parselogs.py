#!/usr/bin/env python3
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

import argparse
import configparser
import fcntl
import re
import sys
from os import makedirs, path
from typing import IO, Dict  # noqa

# Make this work from git.
if path.exists(path.join(path.dirname(__file__), '../..', '.git')):
    sys.path.insert(0, path.join(path.dirname(__file__), '../..'))

from cslbot.helpers.orm import Log  # noqa
from cslbot.helpers.sql import get_session  # noqa


class LogProcesser:

    def __init__(self, outdir: str) -> None:
        self.day: dict[str, str] = {}
        self.logs: dict[str, IO] = {}
        self.outdir = outdir

    def __del__(self):
        for log in self.logs.values():
            log.close()

    def get_path(self, channel: str) -> str:
        if not path.abspath(path.join(self.outdir, channel)).startswith(self.outdir):
            raise Exception("Bailing out due to possible path traversal attack from %s." % channel)
        return path.join(self.outdir, "%s.log" % re.sub(r'[^\w#\-_\. ]', '_', channel))

    def check_day(self, row: Log) -> None:
        # FIXME: print out new day messages for each day, not just the most recent one.
        channel = f'{row.server}.{row.target}'
        rowday = row.time.strftime('%d')
        if channel not in self.day:
            self.day[channel] = rowday
            return
        if self.day[channel] != rowday:
            self.day[channel] = rowday
            log = row.time.strftime('New Day: %a, %b %d, %Y')
            self.write_log(channel, log)

    def write_log(self, channel: str, msg: str) -> None:
        if channel not in self.logs:
            outfile = self.get_path(channel)
            self.logs[channel] = open(outfile, 'a', encoding='utf-8')
        self.logs[channel].write(msg + '\n')

    def process_line(self, row: Log) -> None:
        self.check_day(row)
        self.write_log(f'{row.server}.{row.target}', gen_log(row))


def get_id(outdir: str) -> int:
    outfile = path.join(outdir, ".dbid")
    if not path.exists(outfile):
        return 0
    with open(outfile) as f:
        return int(f.read())


def save_id(outdir: str, new_id: int) -> None:
    with open(path.join(outdir, '.dbid'), 'w') as f:
        f.write(str(new_id) + '\n')


def gen_log(row: Log) -> str:
    logtime = row.time.strftime('%Y-%m-%d %H:%M:%S')
    nick = row.source.split('!')[0]
    if row.type == 'join':
        log = f'{logtime} --> {nick} ({row.source}) has joined {row.target}'
    elif row.type == 'part':
        log = f'{logtime} <-- {nick} ({row.source}) has left {row.target}'
        if row.msg:
            log = f"{log} ({row.msg})"
    elif row.type == 'quit':
        log = f'{logtime} <-- {nick} ({row.source}) has quit ({row.msg})'
    elif row.type == 'kick':
        args = row.msg.split()
        log = '{} <-- {} has kicked {} ({})'.format(logtime, nick, args[0], " ".join(args[1:]))
    elif row.type == 'action':
        log = f'{logtime} * {nick} {row.msg}'
    elif row.type == 'mode':
        log = f'{logtime} Mode {row.target} [{row.msg}] by {nick}'
    elif row.type == 'nick':
        log = f'{logtime} -- {nick} is now known as {row.msg}'
    elif row.type == 'topic':
        # FIXME: keep track of the old topic
        log = f'{logtime} {nick} has changed topic for {row.target} to "{row.msg}"'
    elif row.type in ['pubnotice', 'privnotice']:
        log = f'{logtime} Notice({nick}): {row.msg}'
    elif row.type in ['privmsg', 'pubmsg']:
        if bool(row.flags & 1):
            nick = '@' + nick
        if bool(row.flags & 2):
            nick = '+' + nick
        log = f'{logtime} <{nick}> {row.msg}'
    else:
        raise Exception("Invalid type %s." % row.type)
    return log


def main(confdir: str = "/etc/cslbot") -> None:
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(path.join(confdir, 'config.cfg')) as f:
        config.read_file(f)
    session = get_session(config)()
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir', help='The directory to write logs too.')
    cmdargs = parser.parse_args()
    if not path.exists(cmdargs.outdir):
        makedirs(cmdargs.outdir)
    lockfile = open(path.join(cmdargs.outdir, '.lock'), 'w')
    fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    current_id = get_id(cmdargs.outdir)
    new_id = session.query(Log.id).order_by(Log.id.desc()).limit(1).scalar()
    # Don't die on empty log table.
    if new_id is None:
        new_id = 0
    save_id(cmdargs.outdir, new_id)
    processer = LogProcesser(cmdargs.outdir)
    for row in session.query(Log).filter(new_id >= Log.id).filter(Log.id > current_id).order_by(Log.time, Log.id).all():
        processer.process_line(row)
    del processer
    fcntl.lockf(lockfile, fcntl.LOCK_UN)
    lockfile.close()


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    main(path.join(path.dirname(__file__), '../..'))
