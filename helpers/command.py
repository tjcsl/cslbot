# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi,
# Samuel Damashek, James Forcier, and Reed Koser
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

import sys
import functools
import re
import threading
from . import modutils
from inspect import getdoc
from datetime import datetime, timedelta
from .traceback import handle_traceback
from .thread import start
from .orm import Commands, Log

_known_commands = {}
_disabled_commands = set()


def scan_for_commands(folder):
    """ Scans folder for commands """
    global _known_commands, _disabled_commands
    _known_commands = {}
    _disabled_commands = modutils.get_disabled("commands")
    modutils.scan_and_reimport(folder, "commands")
    return _known_commands


def is_registered(command_name):
    return command_name in _known_commands


def get_command(command_name):
    return _known_commands[command_name]


def get_commands():
    return _known_commands


def get_enabled_commands():
    return [x for x in _known_commands if x not in _disabled_commands]


def get_disabled_commands():
    return [x for x in _known_commands if x in _disabled_commands]


def disable_command(command):
    """ adds a command to the disabled comands list"""
    global _disabled_commands
    if ("commands." + command) not in sys.modules:
        return command + " is not a loaded module"
    if command not in _disabled_commands:
        _disabled_commands.add(command)
        return "Disabled command " + command
    else:
        return "That command is already disabled!"


def enable_command(command):
    """ removes a command from the disabled commands list"""
    global _disabled_commands
    if command == "all":
        _disabled_commands = []
        return "Enabled all modules."
    elif command in _disabled_commands:
        _disabled_commands.remove(command)
        return command + " reenabled"
    else:
        return "That command isn't disabled!"


def record_command(cursor, nick, command, channel):
    record = Commands(nick=nick, command=command, channel=channel)
    cursor.add(record)


def check_command(cursor, nick, msg, target):
    # only care about the last 10 seconds.
    limit = datetime.now() - timedelta(seconds=10)
    # the last one is the command we're currently executing, so get the penultimate one.
    last = cursor.query(Log).filter(Log.target == target, Log.type == 'pubmsg', Log.time >= limit.timestamp()).order_by(Log.time.desc()).offset(1).first()
    if last:
        return last.msg == msg and last.source != nick
    else:
        return False


class Command():

    def __init__(self, names, args=[], limit=0):
        global _known_commands
        self.names = [names] if isinstance(names, str) else names
        self.args = args
        self.limit = limit
        for t in self.names:
            if t in _known_commands:
                raise ValueError("There is already a command registered with the name %s" % t)
            _known_commands[t] = self

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(send, msg, args):
            try:
                thread = threading.current_thread()
                thread_id = re.match('Thread-[0-9]+', thread.name).group(0)
                thread.name = thread_id + " running command." + self.names[0]
                with self.handler.db.session_scope() as args['db']:
                    func(send, msg, args)
            except Exception as ex:
                handle_traceback(ex, self.handler.connection, self.target, self.handler.config, "commands.%s" % self.names[0])
            finally:
                thread.name =  thread_id + " last ran command." + self.names[0]
        self.doc = getdoc(func)
        if self.doc is None or len(self.doc) < 5:
            print("Warning:", self.names[0], "has no or very little documentation")
        self.exe = wrapper
        return wrapper

    def run(self, send, msg, args, command, nick, target, handler):
        if command in _disabled_commands:
            send("Sorry, that command is disabled.")
        else:
            self.target = target
            self.handler = handler
            with handler.db.session_scope() as session:
                record_command(session, nick, command, target)
            start(self.exe, send, msg, args)

    def get_doc(self):
        return self.doc

    def is_limited(self):
        return self.limit != 0
