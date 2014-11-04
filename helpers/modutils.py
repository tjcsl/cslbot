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
from configparser import ConfigParser
import fnmatch
import os
from os.path import basename, dirname
import importlib
from glob import glob

GROUPS = {'commands': set(), 'hooks': set()}


def init_groups(groups):
    # FIXME: validate that all commands/hooks are in groups.cfg exactly once.
    config = ConfigParser()
    config.read_file(open(dirname(__file__)+'/groups.cfg'))
    enabled_command_groups = [x.strip() for x in groups['commands'].split(',')]
    command_group = parse_group(config['commands'])
    for name, values in command_group.items():
        if name not in enabled_command_groups:
            continue
        for x in values:
            GROUPS['commands'].add(x)
    enabled_hook_groups = [x.strip() for x in groups['hooks'].split(',')]
    hook_group = parse_group(config['hooks'])
    for name, values in hook_group.items():
        if name not in enabled_hook_groups:
            continue
        for x in values:
            GROUPS['hooks'].add(x)


def parse_group(cfg):
    groups = {}
    for group in cfg.keys():
        groups[group] = [x.strip() for x in cfg[group].split(',')]
    return groups


def group_enabled(mod_type, name):
    if mod_type == 'helpers':
        return True
    return name in GROUPS[mod_type]

def filename_to_modname(fname, mod_type):
    fname = os.path.splitext(fname)[0] # remove .py
    directories = []
    while True:
        fnames = os.path.split(fname)
        if fnames[1] == '':
            break
        fname = fnames[0]
        directories.append(os.path.split(fname)[1])
    directories = directories[::-1]
    while directories[0] != mod_type:
        directories = directories[1:]
    return '.'.join(directories)

def get_enabled(moddir, mod_type):
    mods = []
    roots = []
    # get the common root directory
    root_dir = os.path.dirname(__file__)
    for root, dirnames, filenames in os.walk(moddir):
        # We don't want to grab the pyc file in the pycache
        if root == '__pycache__':
            continue

        for filename in fnmatch.filter(filenames, '*.py'):
            name = os.path.splitext(basename(filename))[0]
            if group_enabled(mod_type, name):
                modname = filename_to_modname(os.path.join(root, filename), mod_type)
                mods.append(modname + '.' + name)
    return mods


def scan_and_reimport(folder, mod_type):
    """ Scans folder for modules."""
    for mod_name in get_enabled(folder, mod_type):
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)
