# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi,
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
from inspect import getdoc
from datetime import datetime, timedelta
from helpers.modutils import scan_and_reimport
from helpers.traceback import handle_traceback

_known_commands = {}
_disabled_commands = []


def scan_for_commands(folder):
    """ Scans folder for commands """
    global _known_commands
    _known_commands = {}
    scan_and_reimport(folder, "commands")
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
        _disabled_commands.append(command)
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
    cursor.execute('INSERT INTO commands(nick,command,channel) VALUES(?,?,?)', (nick, command, channel))


def check_command(cursor, nick, msg, target):
    # only care about the last 10 seconds.
    limit = datetime.now() - timedelta(seconds=10)
    # the last one is the command we're current executing, so get the penultimate one.
    last = cursor.execute('SELECT msg,source FROM log WHERE target=? AND type="pubmsg" AND time>=? ORDER BY time DESC LIMIT 2', (target, limit.timestamp())).fetchall()
    if len(last) == 2:
        last = last[1]
        return last['msg'] == msg and last['source'] != nick
    else:
        return False


class Command():
    def __init__(self, names, args=[], limit=0):
        global _known_commands
        self.names = [names] if type(names) == str else names
        self.args = args
        self.limit = limit
        for t in self.names:
            if t in _known_commands:
                raise ValueError("There is already a command registered with the name %s" % t)
            _known_commands[t] = self

    def __call__(self, func):
        def wrapper(send, msg, args):
            try:
                func(send, msg, args)
            except Exception as ex:
                handle_traceback(ex, self.c, self.target)
        self.doc = getdoc(func)
        if self.doc is None or len(self.doc) < 5:
            print("Warning:", self.names[0], "has no or very little documentation")
        self.exe = wrapper
        return wrapper

    def run(self, send, msg, args, command, nick, target, handler):
        if command in _disabled_commands:
            send("Sorry, that command is disabled.")
        else:
            self.c = handler.connection
            self.target = target
            record_command(handler.db.get(), nick, command, target)
            handler.executor.submit(self.exe, send, msg, args)

    def get_doc(self):
        return self.doc

    def is_limited(self):
        return self.limit != 0
