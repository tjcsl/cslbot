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
from os.path import basename, dirname
import importlib
from glob import glob

GROUPS = {'commands': set(), 'hooks': set()}
AUX = {'commands': [], 'hooks': [], 'helpers': []}


def init_aux(commands):
    AUX['commands'] = [x.strip() for x in commands.split(',')]


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


def get_enabled(moddir, mod_type):
    mods = []
    for f in glob(moddir + '/*.py'):
        name = basename(f).split('.')[0]
        if group_enabled(mod_type, name):
            mod_pkg = moddir.replace('/', '.')
            mods.append("%s.%s" % (mod_pkg, name))
    return mods


def get_modules(folder, mod_type):
    core_modules = get_enabled(folder, mod_type)
    for aux in AUX[mod_type]:
        core_modules.extend(get_enabled(aux, mod_type))
    return core_modules


def scan_and_reimport(folder, mod_type):
    """ Scans folder for modules."""
    for mod in get_modules(folder, mod_type):
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
        else:
            importlib.import_module(mod)
