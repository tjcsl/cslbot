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
from datetime import datetime, timedelta
from inspect import getdoc
from typing import Any, Callable, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from . import backtrace, registry
from .orm import Commands, Log


def record_command(cursor: Session, nick: str, command: str, channel: str) -> None:
    record = Commands(nick=nick, command=command, channel=channel)
    cursor.add(record)


def check_command(cursor: Session, nick: str, msg: str, target: str) -> bool:
    # only care about the last 10 seconds.
    limit = datetime.now() - timedelta(seconds=10)
    # the last one is the command we're currently executing, so get the penultimate one.
    last = cursor.query(Log).filter(Log.target == target, Log.type == 'pubmsg', Log.time >= limit).order_by(Log.time.desc()).offset(1).first()
    if last:
        return bool(last.msg == msg and last.source != nick)
    else:
        return False


class Command(object):

    def __init__(self, names: Union[str, list], args: List[str] = [], limit: int = 0, role: Optional[str] = None) -> None:
        self.names: List[str] = [names] if isinstance(names, str) else names
        self.args = args
        self.limit = limit
        self.required_role = role
        for name in self.names:
            registry.command_registry.register(self, name)

    def __call__(self, func: Callable[[Callable[[str], None], str, Dict[str, str]], None]) -> Callable[[str], None]:

        @functools.wraps(func)
        def wrapper(send, msg: str, args: Dict[str, str]) -> None:
            try:
                thread = threading.current_thread()
                match = re.match(r'ThreadPool_\d+', thread.name)
                thread_id = "Unknown" if match is None else match.group(0)
                thread.name = "%s running command.%s" % (thread_id, self.names[0])
                with self.handler.db.session_scope() as args['db']:
                    func(send, msg, args)
            except Exception as ex:
                backtrace.handle_traceback(ex, self.handler.connection, self.target, self.handler.config, "commands.%s" % self.names[0])
            finally:
                thread.name = "%s idle, last ran command.%s" % (thread_id, self.names[0])

        self.doc = getdoc(func)
        if self.doc is None or len(self.doc) < 5:
            print("Warning:", self.names[0], "has no or very little documentation")
        self.exe = wrapper
        return wrapper

    def __str__(self) -> str:
        return self.names[0]

    def __repr__(self) -> str:
        return self.names[0]

    def run(self, send: Callable[[str], None], msg: str, args: Dict[str, Any], command: str, nick: str, target: str, handler) -> None:
        if [x for x in self.names if registry.command_registry.is_disabled(x)]:
            send("Sorry, that command is disabled.")
        else:
            self.target = target
            self.handler = handler
            with handler.db.session_scope() as session:
                record_command(session, nick, command, target)
            handler.workers.start_thread(self.exe, send, msg, args)

    def get_doc(self) -> Optional[str]:
        return self.doc

    def is_limited(self) -> bool:
        return self.limit != 0
