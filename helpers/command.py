# -*- coding: utf-8 -*-
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi,
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
from helpers.modutils import scan_and_reimport

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
    elif command in _disabled_commands:
        del _disabled_commands[command]
        return command + " reenabled"
    else:
        return "that command isn't disabled!"


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
            func(send, msg, args)
        self.doc = getdoc(func)
        self.exe = wrapper
        return wrapper

    def run(self, send, msg, args, name):
        if name in _disabled_commands:
            send("Sorry, that command is disabled.")
        else:
            self.exe(send, msg, args)

    def get_doc(self):
        return self.doc

    def is_limited(self):
        return self.limit != 0
