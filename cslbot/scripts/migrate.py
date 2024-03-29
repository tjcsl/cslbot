#!/usr/bin/env python3
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from os.path import dirname, exists, join
from sys import path

# Make this work from git.
if exists(join(dirname(__file__), '../../.git')):
    path.insert(0, join(dirname(__file__), '../..'))

from alembic import command, config  # noqa


def main(confdir: str = "/etc/cslbot") -> None:
    conf_obj = config.Config(join(confdir, 'config.cfg'))
    command.upgrade(conf_obj, 'head')


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    main(join(dirname(__file__), '../..'))
