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
from os.path import exists, dirname, join
from pkg_resources import Requirement, resource_string


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

    admins = ""
    while not check_admins(admins, nickregex):
        admins = input(prompttext % "comma-delimited list of admins")
    config['auth']['admins'] = admins


def check_admins(admins, nickregex):
    admins = [x.strip() for x in admins.split(',')]
    for x in admins:
        if not re.match(nickregex, x):
            return False
    return True


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
