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
import os
import importlib
import imp
from os.path import basename
from glob import glob

_known_commands = {}
_disabled_commands = {}


def scan_for_commands(folder):
    """ Scans folder for commands """
    global _known_commands
    _known_commands = {}
    for f in glob(folder + '/*.py'):
        if os.access(f, os.X_OK):
            cmd = basename(f).split('.')[0]
            #We only need to run import_module, the command decorator constructor
            #will take care of the rest
            mod_name = "commands." + cmd
            if mod_name in sys.modules:
                imp.reload(sys.modules[mod_name])
            else:
                importlib.import_module(mod_name)
    return _known_commands


def is_registered(command_name):
    return command_name in _known_commands


def get_command(command_name):
    return _known_commands[command_name]


def disable_command(command):
    """ adds a command to the disabled comands list"""
    global _disabled_commands
    if ("commands." + command) not in sys.modules:
        return command + " is not a loaded module"
    if command not in _disabled_commands:
        _disabled_commands[command] = "disabled"
        return "Disabled command " + command
    else:
        return "That command is already disabled!"


def enable_command(command):
    """ removes a command from the disabled commands list"""
    global _disabled_commands
    if command in _disabled_commands:
        del _disabled_commands[command]
        return command + " reenabled"
    else:
        return "that command isn't disabled!"


class Command():
    def __init__(self, names, args=[], limit=0):
        global _known_commands
        if isinstance(names, list):
            self.names = names
        else:
            self.names = [names]
        self.args = args
        self.limit = limit
        for t in self.names:
            if t in _known_commands:
                raise ValueError("There is already a command registered with the name %s, is %s" % (t, str(_known_commands[t])))
            _known_commands[t] = self

    def __call__(self, func):
        def wrapper(send, msg, args):
            func(send, msg, args)
        self.exe = wrapper
        return wrapper

    def run(self, send, msg, args):
        self.exe(send, msg, args)

    def is_limited(self):
        return self.limit != 0
