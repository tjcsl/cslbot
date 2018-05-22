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

import multiprocessing
import re
import signal
import threading
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Any, Callable, Dict  # noqa

import concurrent.futures

from sqlalchemy import or_

from . import babble, backtrace, control
from .orm import Log
from ..commands import quote

executor_lock = threading.Lock()

Event = namedtuple("Event", ["event", "run_on_cancel"])


def pool_init():
    """We ignore Ctrl-C in the pool workers, so that we can clean things up properly."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class Workers(object):

    def __init__(self, handler) -> None:
        self.worker_lock = threading.Lock()
        with self.worker_lock:
            self.pool = multiprocessing.Pool(initializer=pool_init)
            self.events: Dict[int, Event] = {}
        with executor_lock:
            self.executor = concurrent.futures.ThreadPoolExecutor(4)
        self.handler = handler

        def send(msg, target=handler.config["core"]["ctrlchan"]):
            handler.send(target, handler.config["core"]["nick"], msg, "privmsg")

        self.defer(3600, False, self.handle_pending, handler, send)
        self.defer(3600, False, self.update_babble, handler, send)
        self.defer(3600, False, self.check_active, handler, send)
        self.defer(3600, False, self.send_quotes, handler, send)

    def start_thread(self, func, *args, **kwargs):
        with executor_lock:
            self.executor.submit(func, *args, **kwargs)

    def run_pool(self, func, args):
        with self.worker_lock:
            result = self.pool.apply_async(func, args)
        return result

    def restart_pool(self):
        with self.worker_lock:
            self.pool.terminate()
            self.pool.join()
            self.pool = multiprocessing.Pool(initializer=pool_init)

    def run_action(self, func, args):
        try:
            thread = threading.current_thread()
            thread_id = re.match(r"Thread-\d+", thread.name)
            if thread_id is None:
                raise Exception("Invalid thread name {}".format(thread.name))
            thread_id = thread_id.group(0)
            thread.name = "%s running %s" % (thread_id, func.__name__)
            func(*args)
        except Exception as ex:
            ctrlchan = self.handler.config["core"]["ctrlchan"]
            backtrace.handle_traceback(ex, self.handler.connection, ctrlchan, self.handler.config)

    def defer(
        self, t: int, run_on_cancel: bool, func: Callable[[Any, Any], None], *args: Any
    ) -> int:
        event = threading.Timer(t, self.run_action, kwargs={"func": func, "args": args})
        event.name = "%s deferring %s" % (event.name, func.__name__)
        event.start()
        with self.worker_lock:
            self.events[event.ident] = Event(event, run_on_cancel)
        return event.ident

    def cancel(self, eventid):
        with self.worker_lock:
            self.events[eventid].event.cancel()
            if self.events[eventid].run_on_cancel:
                self.events[eventid].event.function(**self.events[eventid].event.kwargs)
            del self.events[eventid]

    def stop_workers(self, clean):
        """Stop workers and deferred events."""
        with executor_lock:
            self.executor.shutdown(clean)
            del self.executor
        with self.worker_lock:
            if clean:
                self.pool.close()
            else:
                self.pool.terminate()
            self.pool.join()
            del self.pool
            for x in self.events.values():
                x.event.cancel()
            self.events.clear()

    def handle_pending(self, handler, send):
        # Re-schedule handle_pending
        self.defer(3600, False, self.handle_pending, handler, send)
        with handler.db.session_scope() as session:
            control.show_pending(session, send, True)

    def send_quotes(self, handler, send):
        # Re-schedule send_quotes
        # THE MASSES MUST BE APPEASED
        self.defer(3600 * 24, False, self.send_quotes, handler, send)
        with handler.db.session_scope() as session:
            channel = self.handler.config["core"]["channel"]
            send("QOTD: {}".format(quote.do_get_quote(session)), target=channel)

    def check_active(self, handler, send):
        # Re-schedule check_active
        self.defer(3600, False, self.check_active, handler, send)
        if not self.handler.config.getboolean("feature", "voiceactive"):
            return
        # Mark inactive after 24 hours.
        active_time = datetime.now() - timedelta(hours=24)
        with handler.db.session_scope() as session:
            with handler.data_lock:
                for name in handler.channels.keys():
                    for nick, voiced in handler.voiced[name].items():
                        if (
                            voiced
                            and session.query(Log).filter(
                                Log.source == nick,
                                Log.time >= active_time,
                                or_(Log.type == "pubmsg", Log.type == "action"),
                            ).count()
                            == 0
                        ):
                            handler.rate_limited_send("mode", name, "-v %s" % nick)

    def update_babble(self, handler, send):
        # Re-schedule update_babble
        self.defer(3600, False, self.update_babble, handler, send)
        with handler.db.session_scope() as session:
            babble.update_markov(session, handler.config)
