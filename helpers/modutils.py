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
import os
from os.path import basename
import importlib
import imp
from glob import glob


def get_enabled(moddir):
    mods = []
    for f in glob(moddir + '/*.py'):
        if os.access(f, os.X_OK):
            mods.append(basename(f).split('.')[0])
    return mods


def scan_and_reimport(folder, mod_pkg):
    """ Scans folder for hooks """
    for mod in get_enabled(folder):
        mod_name = mod_pkg + "." + mod
        if mod_name in sys.modules:
            imp.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)
