# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from threading import Lock, Timer
from .control import show_pending

_lock = Lock()
_events = {}


def defer(t, func, *args):
    event = Timer(t, func, args)
    event.start()
    with _lock:
        _events[event.ident] = event
    return event.ident


def cancel(eventid):
    with _lock:
        _events[eventid].cancel()
        del _events[eventid]


def stop_workers():
    with _lock:
        for event in _events.values():
            event.cancel()
        _events.clear()


def start_workers(handler):
    # Set-up notifications for pending admin approval.
    send = lambda msg, target=handler.config['core']['ctrlchan']: handler.send(target, handler.config['core']['nick'], msg, 'privmsg')
    # the scheduler immediately exits if there are no pending tasks.
    defer(3600, handle_pending, handler, send)


def handle_pending(handler, send):
    # Re-schedule handle_pending
    defer(3600, handle_pending, handler, send)
    admins = ": ".join(handler.admins)
    cursor = handler.db.get()
    show_pending(cursor, admins, send, True)
