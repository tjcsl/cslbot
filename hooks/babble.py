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

from threading import Lock
from helpers.hook import Hook
from helpers.orm import Babble
from helpers.babble import build_markov

babble_lock = Lock()


def update_markov(handler, config):
    with babble_lock:
        with handler.db.session_scope() as cursor:
            cmdchar = config['core']['cmdchar']
            ctrlchan = config['core']['ctrlchan']
            build_markov(cursor, cmdchar, ctrlchan)


@Hook('babble', ['pubmsg', 'privmsg'], ['db', 'handler', 'config'])
def hook(send, msg, args):
    # No babble cache, nothing to update
    if not args['db'].query(Babble).count():
        return
    # FIXME: move to check_babble?
    args['handler'].workers.defer(0, False, update_markov, args['handler'], args['config'])
