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

from .modutils import scan_and_reimport
from .traceback import handle_traceback
from .thread import start
from sqlalchemy.exc import InternalError

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

    def __init__(self, types, args=[]):
        global _known_hooks
        self.types = [types] if type(types) == str else types
        self.args = args
        _known_hooks.append(self)

    def __call__(self, func):
        def wrapper(send, msg, msgtype, args):
            if msgtype in self.types:
                try:
                    func(send, msg, args)
                except InternalError:
                    raise
                except Exception as ex:
                    handle_traceback(ex, self.handler.connection, self.target, self.handler.config, func.__module__)
        self.exe = wrapper
        self.name = func.__module__.split('.')[1]
        return wrapper

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def run(self, send, msg, msgtype, handler, target, args):
        self.handler = handler
        self.target = target
        start(self.exe, send, msg, msgtype, args)
