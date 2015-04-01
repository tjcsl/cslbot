# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import threading
import re
from helpers.command import Command


@Command('threads')
def cmd(send, msg, args):
    """Enumerate threads.
    Syntax: !threads
    """
    for x in sorted(threading.enumerate(), key=lambda k: k.name):
        #Handle the threads with a 'func' kwarg (handle_pending and check_babble)
        if hasattr(x, 'kwargs') and 'func' in x.kwargs:
            send(re.match('Thread-[0-9]+', x.name).group(0) + " running " + x.kwargs['func'].__name__)
        #Handle the main server thread (permanently listed as _worker)
        elif re.match('Thread-[0-9]+$', x.name) and x._target.__name__ == '_worker':
            send(x.name + " running main server")
        #Handle the pool threads (they don't have names beyond Thread-x)
        elif re.match('Thread-[0-9]+$', x.name):
            send(x.name + " running " + x._target.__name__)
        #Handle everything else (these are threads which we name elsewhere and MainThread)
        else:
            send(x.name)
