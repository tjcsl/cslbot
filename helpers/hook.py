# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from .traceback import handle_traceback

_known_hooks = {}
_disabled_hooks = set()


def scan_for_hooks(folder):
    """ Scans folder for hooks """
    global _known_hooks, _disabled_hooks
    _known_hooks = {}
    _disabled_hooks = modutils.get_disabled("hooks")
    modutils.scan_and_reimport(folder, "hooks")
    return _known_hooks


def get_known_hooks():
    return _known_hooks


def get_enabled_hooks():
    return [x for x in _known_hooks if x not in _disabled_hooks]


def get_disabled_hooks():
    return [x for x in _known_hooks if x in _disabled_hooks]


def disable_hook(hook):
    """Adds a hook to the disabled hooks list."""
    global _disabled_hooks
    if ("hooks.%s" % hook) not in sys.modules:
        return "%s is not a loaded hook" % hook
    if hook not in _disabled_hooks:
        _disabled_hooks.add(hook)
        return "Disabled hook %s" % hook
    else:
        return "That hook is already disabled!"


def enable_hook(hook):
    """Removes a command from the disabled hooks list."""
    global _disabled_hooks
    if hook == "all":
        _disabled_hooks = []
        return "Enabled all hooks."
    elif hook in _disabled_hooks:
        _disabled_hooks.remove(hook)
        return "Enabled hook %s" % hook
    elif ("hooks.%s" % hook) in sys.modules:
        return "That hook isn't disabled!"
    else:
        return "%s is not a loaded hook" % hook


class Hook():

    def __init__(self, name, types, args=[]):
        global _known_hooks
        self.name = name
        self.types = [types] if isinstance(types, str) else types
        self.args = args
        _known_hooks[name] = self

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(send, msg, msgtype, args):
            if msgtype in self.types:
                try:
                    thread = threading.current_thread()
                    thread_id = re.match('Thread-\d+', thread.name).group(0)
                    thread.name = "%s running %s" % (thread_id, func.__module__)
                    with self.handler.db.session_scope() as args['db']:
                        func(send, msg, args)
                except Exception as ex:
                    handle_traceback(ex, self.handler.connection, self.target, self.handler.config, func.__module__)
                finally:
                    thread.name = "%s idle, last ran %s" % (thread_id, func.__module__)
        self.exe = wrapper
        return wrapper

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def run(self, send, msg, msgtype, handler, target, args):
        if self.name in _disabled_hooks:
            return
        self.handler = handler
        self.target = target
        handler.workers.start_thread(self.exe, send, msg, msgtype, args)
