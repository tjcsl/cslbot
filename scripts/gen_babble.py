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

import argparse
import configparser
import time
from os.path import exists, dirname, join
from sys import path

# Make this work from git.
if exists(join(dirname(__file__), '../.git')):
    path.insert(0, join(dirname(__file__), '..'))

from helpers.babble import build_markov
from helpers.sql import get_session


def main(srcdir=None):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    srcdir = srcdir if srcdir is not None else "FIXME"
    with open(join(srcdir, '../config.cfg')) as f:
        config.read_file(f)
    parser = argparse.ArgumentParser()
    parser.add_argument('--nick', help='The nick to generate babble cache for (testing only).')
    args = parser.parse_args()
    session = get_session(config)()
    cmdchar = config['core']['cmdchar']
    ctrlchan = config['core']['ctrlchan']
    print('Generating markov.')
    # FIXME: support locking for other dialects?
    if session.bind.dialect.name == 'postgresql':
        session.execute('LOCK TABLE babble IN EXCLUSIVE MODE NOWAIT')
        session.execute('LOCK TABLE babble_count IN EXCLUSIVE MODE NOWAIT')
        session.execute('LOCK TABLE babble_last IN EXCLUSIVE MODE NOWAIT')
    t = time.time()
    build_markov(session, cmdchar, ctrlchan, args.nick, initial_run=True, debug=True)
    print('Finished markov in %f' % (time.time() - t))


if __name__ == '__main__':
    main(dirname(__file__))
