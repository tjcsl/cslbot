# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
from os.path import abspath, basename, dirname, join
import traceback
import importlib
import logging
from glob import glob

GROUPS = {'commands': set(), 'hooks': set()}
DISABLED = {'commands': set(), 'hooks': set()}
AUX = {'commands': [], 'hooks': []}


def init_aux(config):
    AUX['commands'] = [x.strip() for x in config['extracommands'].split(',')]
    AUX['hooks'] = [x.strip() for x in config['extrahooks'].split(',')]


def init_groups(groups):
    config = ConfigParser()
    with open(dirname(__file__) + '/groups.cfg') as cfgfile:
        config.read_file(cfgfile)
    add_to_groups(config, groups, 'commands')
    add_to_groups(config, groups, 'hooks')


def add_to_groups(config, groups, mod_type):
    enabled_groups = [x.strip() for x in groups[mod_type].split(',')]
    mod_group = parse_group(config[mod_type])
    for name, values in mod_group.items():
        for x in values:
            if loaded(mod_type, x):
                raise Exception('Module %s cannot occur multiple times in groups.cfg' % x)
            if name in enabled_groups:
                GROUPS[mod_type].add(x)
            else:
                DISABLED[mod_type].add(x)


def loaded(mod_type, name):
    return name in GROUPS[mod_type] or name in DISABLED[mod_type]


def parse_group(cfg):
    groups = {}
    for group in cfg.keys():
        groups[group] = [x.strip() for x in cfg[group].split(',')]
    return groups


def group_enabled(mod_type, name):
    if mod_type == 'helpers':
        return True
    return name in GROUPS[mod_type]


def group_disabled(mod_type, name):
    return name in DISABLED[mod_type]


def get_disabled(mod_type):
    return DISABLED[mod_type]


def get_enabled(moddir, mod_type):
    enabled, disabled = [], []
    full_path = abspath(join(dirname(__file__), '..'))
    full_dir = join(full_path, moddir)
    for f in glob(join(full_dir, '*.py')):
        name = basename(f).split('.')[0]
        mod_pkg = moddir.replace('/', '.')
        mod_name = "%s.%s" % (mod_pkg, name)
        if group_enabled(mod_type, name):
            enabled.append(mod_name)
        elif group_disabled(mod_type, name):
            disabled.append(mod_name)
        elif name != '__init__':
            raise Exception("%s must be either enabled or disabled in groups.cfg" % mod_name)
    return enabled, disabled


def get_modules(folder, mod_type):
    core_enabled, core_disabled = get_enabled(folder, mod_type)
    for aux in AUX[mod_type]:
        if not aux:
            continue
        aux_enabled, aux_disabled = get_enabled(aux, mod_type)
        core_enabled.extend(aux_enabled)
        core_disabled.extend(aux_disabled)
    return core_enabled, core_disabled


def safe_reload(modname):
    """ Catch and log any errors that arise from reimporting a module, but do not die.

    :rtype: bool
    :return: True when import was successful
    """
    try:
        importlib.reload(modname)
        return True
    except Exception as e:
        logging.error("Failed to reimport module: %s" % (e))
        (typ3, value, tb) = sys.exc_info()
        errmsg = "".join(traceback.format_exception(typ3, value, tb))
        for line in errmsg.split('\n'):
            logging.error(errmsg)
        return False


def safe_load(modname):
    """ Load a module, logging errors instead of dying if it fails to load

    :rtype: bool
    :return: True when import was successful
    """
    try:
        importlib.import_module(modname)
        return True
    except Exception as e:
        logging.error("Failed to import module: %s" % (e))
        (typ3, value, tb) = sys.exc_info()
        errmsg = "".join(traceback.format_exception(typ3, value, tb))
        for line in errmsg.split('\n'):
            logging.error(errmsg)
        return False


def scan_and_reimport(folder, mod_type):
    """ Scans folder for modules."""
    mod_enabled, mod_disabled = get_modules(folder, mod_type)
    errors = []
    for mod in (mod_enabled + mod_disabled):
        if mod in sys.modules:
            if not safe_reload(sys.modules[mod]):
                errors.append(mod)
        else:
            if not safe_load(mod):
                errors.append(mod)
    return errors
