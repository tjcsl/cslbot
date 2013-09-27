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
from os.path import basename
import importlib
import imp
from glob import glob

_known_hooks = []


def scan_for_hooks(folder):
    """ Scans folder for hooks """
    global _known_hooks
    _known_hooks = []
    for f in glob(folder + '/*.py'):
        if os.access(f, os.X_OK):
            cmd = basename(f).split('.')[0]
            #We only need to run import_module, the hook decorator constructor
            #will take care of the rest
            mod_name = "hooks." + cmd
            if mod_name in sys.modules:
                imp.reload(sys.modules[mod_name])
            else:
                importlib.import_module(mod_name)
    return _known_hooks


class Hook():

    def __init__(self, types, reqargs):
        global _known_hooks
        self.types = types
        self.reqargs = reqargs
        _known_hooks.append(self)

    def __call__(self, func):
        def wrapper(send, msg, msgtype, args):
            if msgtype in self.types:
                func(send, msg, args)
        self.exe = wrapper
        return wrapper

    def run(self, send, msg, msgtype, args):
        self.exe(send, msg, msgtype, args)
