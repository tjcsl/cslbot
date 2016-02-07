# -*- coding: utf-8 -*-
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

import configparser
import re
from os import mkdir
from os.path import dirname, exists, join

from pkg_resources import Requirement, resource_string

from typing import Callable


def migrate_config(config_file, config_obj, send):
    example_obj = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    example_obj.read_string(resource_string(Requirement.parse('CslBot'), 'cslbot/static/config.example').decode())
    modified = False

    # Check for new sections/options
    for section in example_obj.sections():
        if not config_obj.has_section(section):
            send("Adding config section %s" % section)
            config_obj.add_section(section)
            modified = True
        for option in example_obj.options(section):
            if not config_obj.has_option(section, option):
                send("Adding default value for config option %s.%s" % (section, option))
                config_obj[section][option] = example_obj[section][option]
                modified = True
    # Check for removed sections/options
    for section in config_obj.sections():
        if example_obj.has_section(section):
            for option in config_obj.options(section):
                if not example_obj.has_option(section, option):
                    send("Obsolete config option %s.%s, consider removing." % (section, option))
        else:
            send("Obsolete config section %s, consider removing." % section)
    if modified:
        send("Config file automatically migrated, please review.")
        with open(config_file, 'w') as f:
            config_obj.write(f)


def load_config(config_file: str, send: Callable[[str], None]) -> configparser.ConfigParser:
    config_obj = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(config_file) as f:
        config_obj.read_file(f)
    migrate_config(config_file, config_obj, send)
    return config_obj


def do_config(config):
    nickregex = config['core']['nickregex']
    channelregex = "#[^ ,]{1,49}"
    prompttext = "Please enter a valid %s for the bot: "

    nick = ""
    while not re.match(nickregex, nick):
        nick = input(prompttext % "nick")
    config['core']['nick'] = nick

    channel = ""
    while not re.match(channelregex, channel):
        channel = input(prompttext % "primary channel")
    config['core']['channel'] = channel

    controlchannel = ""
    while not re.match(channelregex, controlchannel):
        controlchannel = input(prompttext % "control channel")
    config['core']['ctrlchan'] = controlchannel

    owner = ""
    while not re.match(nickregex, owner):
        owner = input(prompttext % "nick of owner")
    config['auth']['owner'] = owner


def do_setup(configfile):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read_string(resource_string(Requirement.parse('CslBot'), 'cslbot/static/config.example').decode())
    do_config(config)
    configdir = dirname(configfile)
    try:
        if not exists(configdir):
            mkdir(configdir)
        with open(configfile, 'w') as cfgfile:
            config.write(cfgfile)
        groupsfile = join(configdir, 'groups.cfg')
        if not exists(groupsfile):
            with open(groupsfile, 'wb') as f:
                f.write(resource_string(Requirement.parse('CslBot'), 'cslbot/static/groups.example'))
    except PermissionError:
        raise Exception("Please make sure that the user you are running CslBot as has permission to write to %s" % configdir)
    print('WARNING: you must set the db.engine option for the bot to work.')
    print("Configuration succeded, please review %s and restart the bot." % configfile)
