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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import functools
import re
import threading

from typing import Callable, List, Union

from . import backtrace, registry


class Hook(object):

    def __init__(self, name: str, types: Union[str, List[str]], args: List[str] = []) -> None:
        self.name = name
        self.types = [types] if isinstance(types, str) else types
        self.args = args
        registry.hook_registry.register(self)

    def __call__(
        self, func: Callable[[Callable[[str], None], str, List[str]], None]
    ) -> Callable[[str], None]:

        @functools.wraps(func)
        def wrapper(send, msg, msgtype, args):
            if msgtype in self.types:
                try:
                    thread = threading.current_thread()
                    thread_id = re.match(r"Thread-\d+", thread.name)
                    thread_id = "Unknown" if thread_id is None else thread_id.group(0)
                    thread.name = "%s running %s" % (thread_id, func.__module__)
                    with self.handler.db.session_scope() as args["db"]:
                        func(send, msg, args)
                except Exception as ex:
                    backtrace.handle_traceback(
                        ex,
                        self.handler.connection,
                        self.target,
                        self.handler.config,
                        func.__module__,
                    )
                finally:
                    thread.name = "%s idle, last ran %s" % (thread_id, func.__module__)

        self.exe = wrapper
        return wrapper

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def run(
        self,
        send: Callable[[str], None],
        msg: str,
        msgtype: str,
        handler,
        target: str,
        args: List[str],
    ) -> None:
        if registry.hook_registry.is_disabled(self.name):
            return
        self.handler = handler
        self.target = target
        handler.workers.start_thread(self.exe, send, msg, msgtype, args)
