#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
import configparser
import subprocess
import sys
from os.path import dirname, join


def main(confdir: str ="/etc/cslbot") -> None:
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open(join(confdir, 'config.cfg')) as f:
        config.read_file(f)
    passwd = config['auth']['ctrlpass']
    port = config['core']['serverport']
    msg = '%s\nreload' % passwd
    try:
        proc = subprocess.run(['nc', 'localhost', port],
                              input=msg,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              check=True)
        output = proc.stdout.splitlines()
        for line in output:
            print(line)
        if output[-1] != "Aye Aye Capt'n":
            sys.exit(1)
    except subprocess.CalledProcessError:
        raise Exception("Could not connect to server, is bot running?")


if __name__ == '__main__':
    # If we're running from a git checkout, override the config path.
    main(join(dirname(__file__), '..'))
