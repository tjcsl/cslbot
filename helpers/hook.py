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

from helpers.modutils import scan_and_reimport
from threading import Thread

_known_hooks = []


def scan_for_hooks(folder):
    """ Scans folder for hooks """
    global _known_hooks
    _known_hooks = []
    scan_and_reimport(folder, "hooks")
    return _known_hooks


def get_known_hooks():
    return _known_hooks


class Hook():

    def __init__(self, types, args):
        global _known_hooks
        self.types = types
        self.args = args
        _known_hooks.append(self)

    def __call__(self, func):
        def wrapper(send, msg, msgtype, args):
            if msgtype in self.types:
                func(send, msg, args)
        self.exe = wrapper
        self.name = func.__module__.split('.')[1]
        return wrapper

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def run(self, send, msg, msgtype, args):
        Thread(target=self.exe, args=(send, msg, msgtype, args), daemon=True).start()
