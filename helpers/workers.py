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

from collections import namedtuple
from threading import Lock, Timer
from .traceback import handle_traceback
from .control import show_pending
from .orm import Babble_last, Log
from sqlalchemy import or_


Event = namedtuple('Event', ['event', 'run_on_cancel'])


class Workers():

    def __init__(self, handler):
        self.lock = Lock()
        self.events = {}
        self.handler = handler
        # Set-up notifications for pending admin approval.

        def send(msg, target=handler.config['core']['ctrlchan']):
            handler.send(target, handler.config['core']['nick'], msg, 'privmsg')
        self.defer(3600, False, self.handle_pending, handler, send)
        self.defer(3600, False, self.check_babble, handler, send)

    def run_action(self, func, args):
        try:
                func(*args)
        except Exception as ex:
            ctrlchan = self.handler.config['core']['ctrlchan']
            handle_traceback(ex, self.handler.connection, ctrlchan, self.handler.config)

    def defer(self, t, run_on_cancel, func, *args):
        event = Timer(t, self.run_action, kwargs={'func': func, 'args': args})
        event.start()
        with self.lock:
            self.events[event.ident] = Event(event, run_on_cancel)
        return event.ident

    def cancel(self, eventid):
        with self.lock:
            self.events[eventid].event.cancel()
            if self.events[eventid].run_on_cancel:
                self.events[eventid].event.function(*self.events[eventid].event.args)
            del self.events[eventid]

    def stop_workers(self):
        with self.lock:
            for x in self.events.values():
                x.event.cancel()
            self.events.clear()

    def handle_pending(self, handler, send):
        # Re-schedule handle_pending
        self.defer(3600, False, self.handle_pending, handler, send)
        admins = ": ".join(handler.admins)
        with handler.db.session_scope() as session:
            show_pending(session, admins, send, True)

    def check_babble(self, handler, send):
        # Re-schedule check_babble
        self.defer(3600, False, self.check_babble, handler, send)
        cmdchar = handler.config['core']['cmdchar']
        ctrlchan = handler.config['core']['ctrlchan']
        with handler.db.session_scope() as session:
            last = session.query(Babble_last).first()
            row = session.query(Log).filter(or_(Log.type == 'pubmsg', Log.type == 'privmsg'), ~Log.msg.startswith(cmdchar), Log.target != ctrlchan).order_by(Log.id.desc()).first()
            if last is None or row is None:
                return
            if last.last != row.id:
                # FIXME: make this less sensitive?
                raise Exception("Last row in babble cache (%d) does not match last row in log (%d)." % (last.last, row.id))
