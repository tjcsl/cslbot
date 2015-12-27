#!/usr/bin/env python3
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
import sys
from os import path
import subprocess
import configparser
import re
from sqlalchemy import or_, func

# Make this work from git.
if path.exists(path.join(path.dirname(__file__), '..', '.git')):
    sys.path.insert(0, path.join(path.dirname(__file__), '..'))

from cslbot.helpers.orm import Log
from cslbot.helpers.sql import get_session


def main(confdir="/etc/cslbot"):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(path.join(confdir, 'config.cfg')) as f:
        config.read_file(f)
    channel = '#tjhsst'
    session = get_session(config)()
    users = session.query(Log.source, func.count(Log.id)).filter(Log.target == channel,
                                                                 or_(Log.type == 'privmsg', Log.type == 'pubmsg', Log.type == 'action')).having(func.count(Log.id) > 100).group_by(Log.source).order_by(func.count(Log.id)).all()
    users = [x[0] for x in users]
    freq = {}
    for user in users:
        lines = session.query(Log.msg).filter(Log.target == channel, Log.source == user, or_(Log.type == 'privmsg', Log.type == 'pubmsg', Log.type == 'action')).all()
        output = '\n'.join([x[0] for x in lines])
        with open('/tmp/foo', 'w') as f:
            f.write(output)
        output = subprocess.check_output(['zpaq', 'add', 'bob', '/tmp/foo', '-test', '-summary'], stderr=subprocess.STDOUT)
        sizes = output.decode().splitlines()[-2]
        before, after = re.match('.*\((.*) -> .* -> (.*)\).*', sizes).groups()
        freq[user] = (len(lines), float(after) / float(before) * 100)
    for k, v in freq.items():
        print("%s: (%d lines) %f" % (k, v[0], v[1]))


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    # main(path.join(path.dirname(__file__), '..'))
    main()
