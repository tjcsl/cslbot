#!/usr/bin/env python3
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from sys import path
from os.path import dirname, exists, join

# Make this work from git.
if exists(join(dirname(__file__), '../.git')):
    path.insert(0, join(dirname(__file__), '..'))

import configparser
from alembic import command, config
from pkg_resources import Requirement, resource_filename


def main(confdir="/etc/cslbot"):
    botconfig = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(join(confdir, 'config.cfg')) as f:
        botconfig.read_file(f)
    conf_obj = config.Config()
    script_location = resource_filename(Requirement.parse('CslBot'), join('cslbot', botconfig['alembic']['script_location']))
    conf_obj.set_main_option('script_location', script_location)
    conf_obj.set_main_option('bot_config_path', confdir)
    command.upgrade(conf_obj, 'head')


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    main(join(dirname(__file__), '..'))
