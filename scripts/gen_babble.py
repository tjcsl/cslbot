#!/usr/bin/python3 -O
# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, Reed Koser, and James Forcier
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
import time
from configparser import ConfigParser
from os.path import dirname
from sys import path

# HACK: allow sibling imports
path.append(dirname(__file__) + '/..')

from helpers.sql import get_session
import pyximport
pyximport.install()
from helpers.babble import build_markov


def main(config, speaker):
    session = get_session(config)()
    cmdchar = config['core']['cmdchar']
    ctrlchan = config['core']['ctrlchan']
    print('Generating markov.')
    session.execute('LOCK TABLE babble IN EXCLUSIVE MODE')
    session.execute('LOCK TABLE babble_count IN EXCLUSIVE MODE')
    session.execute('LOCK TABLE babble_last IN EXCLUSIVE MODE')
    t = time.time()
    build_markov(session, cmdchar, ctrlchan, speaker, initial_run=True)
    print('Markov built in %f' % (time.time()-t))


if __name__ == '__main__':
    config = ConfigParser()
    config.read_file(open(dirname(__file__) + '/../config.cfg'))
    parser = argparse.ArgumentParser()
    parser.add_argument('--nick', help='The nick to generate babble cache for (testing only).')
    args = parser.parse_args()
    main(config, args.nick)
