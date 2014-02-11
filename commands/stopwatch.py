# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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

from time import time
from datetime import timedelta
from helpers.orm import Stopwatches
from helpers.command import Command


def create_sw(session):
    row = Stopwatches(time=time())
    session.add(row)
    session.flush()
    return "Created new stopwatch with ID %d" % row.id


def get_status(session, sw):
    active = session.query(Stopwatches.active).get(sw).scalar()
    if active is None:
        return "Invalid ID!"
    return "Active" if active == 1 else "Paused"


def get_elapsed(session, sw):
    stopwatch = session.query(Stopwatches).get(sw)
    if stopwatch is None:
        return "No stopwatch exists with that ID!"
    etime = stopwatch.elapsed
    if stopwatch.active == 1:
        etime = time() - stopwatch.time
    return str(timedelta(seconds=etime))


def stop_stopwatch(session, sw):
    stopwatch = session.query(Stopwatches).get(sw)
    if stopwatch is None:
        return "No stopwatch exists with that ID!"
    if stopwatch.active == 0:
        return "That stopwatch is already disabled!"
    etime = stopwatch.elapsed
    etime = time.time() - stopwatch.time
    stopwatch.elapsed = etime
    stopwatch.active = 0
    return "Stopwatch stopped!"


def stopwatch_resume(session, sw):
    stopwatch = session.query(Stopwatches).get(sw)
    if stopwatch is None:
        return "No stopwatch exists with that ID!"
    if stopwatch.active == 1:
        return "That stopwatch is not paused!"
    stopwatch.active = 1
    stopwatch.time = time()
    return "Stopwatch resumed!"


def stopwatch_list(session, send, nick):
    active = session.query(Stopwatches).filter(Stopwatches.active == 1).all()
    paused = session.query(Stopwatches).filter(Stopwatches.active == 0).all()
    send("%d active and %d paused stopwatches." % (len(active), len(paused)))
    for x in active:
        send('Active stopwatch #%d started at %d' % (x.id, x.time), target=nick)
    for x in paused:
        send('Paused stopwatch #%d started at %d time elapsed %d' % (x.id, x.time, x.elapsed), target=nick)


@Command(['stopwatch', 'sw'], ['db', 'nick'])
def cmd(send, msg, args):
    """Start/stops/resume/get stopwatch
    Syntax: !stopwatch <start|stop|resume|get|list>
    """

    if not msg:
        send("Invalid Syntax.")
        return
    msg = msg.split()
    command = msg[0]
    msg = " ".join(msg[1:])
    session = args['db']
    if command == "start":
        send(create_sw(session))
    elif command == "get":
        send("%s %s" % (get_status(session, msg), get_elapsed(session, msg)))
    elif command == "stop":
        send("%s Stopped at %s" % (stop_stopwatch(session, msg), get_elapsed(session, msg)))
    elif command == "resume":
        send(stopwatch_resume(session, msg))
    elif command == "list":
        stopwatch_list(session, send, args['nick'])
    else:
        send("Invalid Syntax.")
