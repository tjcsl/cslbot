#!/usr/bin/python3 -O
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from threading import Thread, Event
from helpers.control import show_issues, show_quotes

_threads = []
event = Event()


def start_workers(handler):
    global _threads, event

    event.set()
    for thread in _threads:
        thread.join()
    event.clear()
    _threads.clear()

    send = lambda msg, target=handler.config['core']['ctrlchan']: handler.send(target, handler.config['core']['nick'], msg, 'privmsg')
    _threads.append(Thread(target=handle_pending, args=(handler, send), daemon=True))
    for thread in _threads:
        thread.start()


def handle_pending(handler, send):
    global event
    admins = ": ".join(handler.admins)
    cursor = handler.db.get()
    while not event.wait(3600):
        issues = cursor.execute('SELECT title,source,id FROM issues WHERE accepted=0').fetchall()
        quotes = cursor.execute('SELECT id,quote,nick,submitter FROM quotes WHERE approved=0').fetchall()
        if issues or quotes:
            send("%s: Items are Pending Approval" % admins)
        if issues:
            send("Issues:")
            show_issues(issues, send)
        if quotes:
            send("Quotes:")
            show_quotes(quotes, send)
