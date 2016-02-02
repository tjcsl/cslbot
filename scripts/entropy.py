#!/usr/bin/env python3
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import configparser  # type: ignore
import json
import re
import subprocess
import sys
from os import path

from sqlalchemy import func, or_  # type: ignore

# Make this work from git.
if path.exists(path.join(path.dirname(__file__), '..', '.git')):
    sys.path.insert(0, path.join(path.dirname(__file__), '..'))

from cslbot.helpers.orm import Log  # noqa
from cslbot.helpers.sql import get_session  # noqa


def main(confdir="/etc/cslbot"):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(path.join(confdir, 'config.cfg')) as f:
        config.read_file(f)
    session = get_session(config)()
    channel = '#tjhsst'
    users = session.query(Log.source).filter(Log.target == channel,
                                             or_(Log.type == 'privmsg', Log.type == 'pubmsg', Log.type == 'action')).having(func.count(Log.id) > 500).group_by(Log.source).all()
    freq = []
    for user in users:
        lines = session.query(Log.msg).filter(Log.target == channel, Log.source == user[0], or_(Log.type == 'privmsg', Log.type == 'pubmsg', Log.type == 'action')).all()
        text = '\n'.join([x[0] for x in lines])
        with open('/tmp/foo', 'w') as f:
            f.write(text)
        output = subprocess.check_output(['zpaq', 'add', 'foo.zpaq', '/tmp/foo', '-test', '-summary', '-method', '5'], stderr=subprocess.STDOUT)
        sizes = output.decode().splitlines()[-2]
        before, after = re.match('.*\((.*) -> .* -> (.*)\).*', sizes).groups()
        # 8 bits = 1 byte
        count = 1024 * 1024 * 8 * float(after) / len(text)
        freq.append((user[0], len(lines), float(after) / float(before) * 100, count))
    with open('freq.json', 'w') as f:
        json.dump(freq, f, indent=True)
    for x in sorted(freq, key=lambda x: x[2]):
        print("%s: (%d lines) (%f%% compressed) (%f bits per char)" % x)


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    # main(path.join(path.dirname(__file__), '..'))
    main()
