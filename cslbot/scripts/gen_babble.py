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

import configparser
import os
import sys
import time

from absl import app, flags
from sqlalchemy import text

FLAGS = flags.FLAGS

flags.DEFINE_string('nick', None, 'The nick to generate babble cache for (testing only).')
flags.DEFINE_bool('incremental', False, 'Whether to build the cache from scratch or incrementally update an existing one.')
flags.DEFINE_string('confdir', '/etc/cslbot', 'Where to read the configuration from.')


def real_main(argv) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected argument(s) received: %s" % argv)
    # If we're running from a git checkout, override paths.
    parent_directory = os.path.join(os.path.dirname(__file__), '../..')
    if os.path.exists(os.path.join(parent_directory, '.git')):
        sys.path.insert(0, parent_directory)
        FLAGS.set_default('confdir', parent_directory)

    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(os.path.join(FLAGS.confdir, 'config.cfg')) as f:
        config.read_file(f)

    from cslbot.helpers import babble, sql
    session = sql.get_session(config)()
    cmdchar = config['core']['cmdchar']
    ctrlchan = config['core']['ctrlchan']
    print('Generating markov.')
    # FIXME: support locking for other dialects?
    if session.bind.dialect.name == 'postgresql':
        session.execute(text('LOCK TABLE babble IN EXCLUSIVE MODE NOWAIT'))
        session.execute(text('LOCK TABLE babble2 IN EXCLUSIVE MODE NOWAIT'))
        session.execute(text('LOCK TABLE babble_count IN EXCLUSIVE MODE NOWAIT'))
        session.execute(text('LOCK TABLE babble_last IN EXCLUSIVE MODE NOWAIT'))
    t = time.time()
    babble.build_markov(session, cmdchar, ctrlchan, FLAGS.nick, initial_run=not FLAGS.incremental, debug=True)
    print('Finished markov in %f' % (time.time() - t))


def main():
    app.run(real_main)


if __name__ == '__main__':
    main()
