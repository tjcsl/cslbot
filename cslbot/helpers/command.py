# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from sqlalchemy.orm import Session

from typing import Any, Callable, Dict, List, Union

from . import backtrace, handler, modutils
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
        return last.msg == msg and last.source != nick
    else:
        return False


class Command(object):

    def __init__(self, names: Union[str, list], args: List[str] =[], limit: int =0, admin: bool =False) -> None:
        self.names = [names] if isinstance(names, str) else names
        self.args = args
        self.limit = limit
        self.admin = admin
        for t in self.names:
            if registry.is_registered(t):
                raise ValueError("There is already a command registered with the name %s" % t)
            registry.register(t, self)

    def __call__(self, func: Callable[[Callable[[str], None], str, Dict[str, str]], None]) -> Callable[[str], None]:
        @functools.wraps(func)
        def wrapper(send, msg: str, args: Dict[str, str]) -> None:
            try:
                thread = threading.current_thread()
                match = re.match(r'Thread-\d+', thread.name)
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

    def run(self, send: Callable[[str], None], msg: str, args: Dict[str, Any], command: str, nick: str, target: str, handler: handler.BotHandler) -> None:
        if [x for x in self.names if registry.is_disabled(x)]:
            send("Sorry, that command is disabled.")
        else:
            self.target = target
            self.handler = handler
            with handler.db.session_scope() as session:
                record_command(session, nick, command, target)
            handler.workers.start_thread(self.exe, send, msg, args)

    def get_doc(self) -> str:
        return self.doc

    def is_limited(self) -> bool:
        return self.limit != 0

    def requires_admin(self) -> bool:
        return self.admin


class CommandData(object):

    def __init__(self) -> None:
        self.known_commands = {}  # type: Dict[str, Command]
        self.disabled_commands = set()  # type: Set[str]

    def scan_for_commands(self) -> List[str]:
        """
        Scans for commands

        :rtype: list
        :return: A list of modules that failed to reload
        """
        self.known_commands.clear()
        self.disabled_commands = modutils.get_disabled("commands")
        errors = modutils.scan_and_reimport("commands")
        return errors

    def get_known_commands(self) -> Dict[str, Command]:
        return self.known_commands

    def get_enabled_commands(self) -> List[str]:
        return [x for x in self.known_commands if x not in self.disabled_commands]

    def get_disabled_commands(self) ->List[str]:
        return [x for x in self.known_commands if x in self.disabled_commands]

    def is_disabled(self, command: str) -> bool:
        return command in self.disabled_commands

    def is_registered(self, command_name: str) -> bool:
        return command_name in self.known_commands

    def get_command(self, command_name: str) -> Command:
        return self.known_commands[command_name]

    def disable_command(self, command: str) -> str:
        """Adds a command to the disabled commands list."""
        if command not in self.known_commands:
            return "%s is not a loaded command" % command
        if command not in self.disabled_commands:
            self.disabled_commands.add(command)
            return "Disabled command %s" % command
        else:
            return "That command is already disabled!"

    def enable_command(self, command: str) -> str:
        """Removes a command from the disabled commands list."""
        if command == "all":
            self.disabled_commands.clear()
            return "Enabled all commands."
        elif command in self.disabled_commands:
            self.disabled_commands.remove(command)
            return "Enabled command %s" % command
        elif command in self.known_commands:
            return "That command isn't disabled!"
        else:
            return "%s is not a loaded command" % command

    def register(self, name: str, command: Command) -> None:
        self.known_commands[name] = command

registry = CommandData()
