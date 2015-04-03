# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import argparse
import re


class ArgumentException(Exception):
    pass


class NickParser(argparse.Action):
    def __call__(self, parser, namespace, value, option_strings):
        if value is None:
            return
        if re.match(namespace.config['core']['nickregex'], value):
            namespace.nick = value
        else:
            raise ArgumentException("Invalid nick %s." % value)


class ArgParser(argparse.ArgumentParser):
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.namespace = argparse.Namespace()
        self.namespace.config = config

    def error(self, message):
        raise ArgumentException(message)

    def parse_args(self, msg):
        return super().parse_args(msg.split(), namespace=self.namespace)
