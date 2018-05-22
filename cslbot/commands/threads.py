# -*- coding: utf-8 -*-
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

import re
import threading

from ..helpers.command import Command


@Command("threads")
def cmd(send, *_):
    """Enumerate threads.

    Syntax: {command}

    """
    thread_names = []
    for x in sorted(threading.enumerate(), key=lambda k: k.name):
        res = re.match(r"Thread-(\d+$)", x.name)
        if res:
            tid = int(res.group(1))
            # Handle the main server thread (permanently listed as _worker)
            if x._target.__name__ == "_worker":
                thread_names.append((tid, "%s running server thread" % x.name))
            # Handle the multiprocessing pool worker threads (they don't have names beyond Thread-x)
            elif x._target.__module__ == "multiprocessing.pool":
                thread_names.append((tid, "%s running multiprocessing pool worker thread" % x.name))
        # Handle everything else including MainThread and deferred threads
        else:
            res = re.match(r"Thread-(\d+)", x.name)
            tid = 0
            if res:
                tid = int(res.group(1))
            thread_names.append((tid, x.name))
    for x in sorted(thread_names, key=lambda k: k[0]):
        send(x[1])
