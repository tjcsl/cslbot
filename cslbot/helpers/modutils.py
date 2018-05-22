# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

import configparser
import importlib
import logging
import sys
import types
from glob import glob
from os.path import basename, join
from typing import Dict, List, Mapping, Set, Tuple, Union

from pkg_resources import Requirement, resource_filename, resource_string

from . import backtrace


class ModuleData(object):

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.groups: Dict[str, Set[str]] = {"commands": set(), "hooks": set()}
        self.disabled: Dict[str, Set[str]] = {"commands": set(), "hooks": set()}
        self.aux: List[str] = []


registry = ModuleData()


def init_aux(config: Mapping[str, str]) -> None:
    registry.reset()
    registry.aux.extend([x.strip() for x in config["extramodules"].split(",")])


def load_groups(confdir: str) -> configparser.ConfigParser:
    example_obj = configparser.ConfigParser()
    example_obj.read_string(
        resource_string(Requirement.parse("CslBot"), "cslbot/static/groups.example").decode()
    )
    config_obj = configparser.ConfigParser()
    with open(join(confdir, "groups.cfg")) as cfgfile:
        config_obj.read_file(cfgfile)
    if config_obj.sections() != example_obj.sections():
        raise Exception(
            "Invalid or missing section in groups.cfg, only valid sections are %s"
            % ",".join(example_obj.sections())
        )
    return config_obj


def init_groups(groups: Mapping[str, str], confdir: str) -> None:
    config = load_groups(confdir)
    add_to_groups(config, groups, "commands")
    add_to_groups(config, groups, "hooks")


def add_to_groups(
    config: configparser.ConfigParser, groups: Mapping[str, str], mod_type: str
) -> None:
    enabled_groups = [x.strip() for x in groups[mod_type].split(",")]
    mod_group = parse_group(config[mod_type])
    for name, values in mod_group.items():
        for x in values:
            if loaded(mod_type, x):
                raise Exception("Module %s cannot occur multiple times in groups.cfg" % x)
            if name in enabled_groups:
                registry.groups[mod_type].add(x)
            else:
                registry.disabled[mod_type].add(x)


def loaded(mod_type: str, name: str) -> bool:
    return name in registry.groups[mod_type] or name in registry.disabled[mod_type]


def parse_group(cfg: Mapping[str, str]) -> Dict[str, List[str]]:
    groups = {}
    for group in cfg.keys():
        groups[group] = [x.strip() for x in cfg[group].split(",")]
    return groups


def group_enabled(mod_type: str, name: str) -> bool:
    if mod_type == "helpers":
        return True
    return name in registry.groups[mod_type]


def group_disabled(mod_type: str, name: str) -> bool:
    return name in registry.disabled[mod_type]


def get_disabled(mod_type: str) -> Set[str]:
    return registry.disabled[mod_type]


def get_enabled(mod_type: str, package="CslBot") -> Tuple[List[str], List[str]]:
    enabled, disabled = [], []
    full_dir = resource_filename(Requirement.parse(package), join(package.lower(), mod_type))
    for f in glob(join(full_dir, "*.py")):
        name = basename(f).split(".")[0]
        mod_name = "%s.%s.%s" % (package.lower(), mod_type, name)
        if group_enabled(mod_type, name):
            enabled.append(mod_name)
        elif group_disabled(mod_type, name):
            disabled.append(mod_name)
        elif name != "__init__":
            logging.error("%s must be either enabled or disabled in groups.cfg" % mod_name)
            # default to disabled
            disabled.append(mod_name)
    return enabled, disabled


def get_modules(mod_type: str) -> Tuple[List[str], List[str]]:
    core_enabled, core_disabled = get_enabled(mod_type)
    for package in registry.aux:
        if not package:
            continue
        aux_enabled, aux_disabled = get_enabled(mod_type, package)
        core_enabled.extend(aux_enabled)
        core_disabled.extend(aux_disabled)
    return core_enabled, core_disabled


def safe_reload(modname: types.ModuleType) -> Union[None, str]:
    """Catch and log any errors that arise from reimporting a module, but do not die.

    :return: None when import was successful. String is the first line of the error message

    """
    try:
        importlib.reload(modname)
        return None
    except Exception as e:
        logging.error("Failed to reimport module: %s", modname)
        msg, _ = backtrace.output_traceback(e)
        return msg


def safe_load(modname: str) -> Union[None, str]:
    """Load a module, logging errors instead of dying if it fails to load.

    :return: None when import was successful. String is the first line of the error message

    """
    try:
        importlib.import_module(modname)
        return None
    except Exception as ex:
        logging.error("Failed to import module: %s", modname)
        msg, _ = backtrace.output_traceback(ex)
        return msg


def scan_and_reimport(mod_type: str) -> List[Tuple[str, str]]:
    """Scans folder for modules."""
    mod_enabled, mod_disabled = get_modules(mod_type)
    errors = []
    for mod in mod_enabled + mod_disabled:
        if mod in sys.modules:
            msg = safe_reload(sys.modules[mod])
        else:
            msg = safe_load(mod)
        if msg is not None:
            errors.append((mod, msg))
    return errors
