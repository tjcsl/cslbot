#!/usr/bin/python3 -O
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

from threading import Event, current_thread, get_ident
from helpers.control import show_pending

_threads = {}


def stop_workers():
    for thread, event in _threads.values():
        event.set()
        thread.join()
    _threads.clear()


def start_workers(handler):
    stop_workers()

    # Set-up notifications for pending admin approval.
    send = lambda msg, target=handler.config['core']['ctrlchan']: handler.send(target, handler.config['core']['nick'], msg, 'privmsg')
    handler.executor.submit(handle_pending, handler, send)


def add_thread(thread):
    global _threads
    _threads[thread.ident] = (thread, Event())


def get_thread(ident):
    return _threads[ident] if ident in _threads.keys() else None


def handle_pending(handler, send):
    admins = ": ".join(handler.admins)
    cursor = handler.db.get()
    add_thread(current_thread())
    while not _threads[get_ident()][1].wait(3600):
        show_pending(cursor, admins, send, True)
