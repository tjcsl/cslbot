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

import argparse
import dateutil.parser
import re
from requests import get


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


class ChanParser(argparse.Action):

    def __call__(self, parser, namespace, value, option_strings):
        if value is None:
            return
        if isinstance(value, str):
            value = [value]
        namespace.channels = []
        for v in value:
            if re.match(namespace.config['core']['chanregex'], v):
                namespace.channels.append(v)
            else:
                raise ArgumentException("Invalid chan %s." % v)


class DateParser(argparse.Action):

    def __call__(self, parser, namespace, value, option_strings):
        if value is None:
            return
        if isinstance(value, list):
            value = ' '.join(value)
        try:
            namespace.date = dateutil.parser.parse(value)
        except (ValueError, OverflowError) as e:
            raise ArgumentException("Couldn't parse a date from %s: %s" % (value, e))


class TumblrParser(argparse.Action):

    def __call__(self, parser, namespace, value, option_strings):
        if value is None:
            return
        if '.' not in value:
            value += ".tumblr.com"
        response = get('http://api.tumblr.com/v2/blog/%s/info' % value, params={'api_key': namespace.config['api']['tumblrconsumerkey']}).json()
        if response['meta']['status'] != 200:
            raise ArgumentException("Error in checking status of blog %s: %s" % (value, response['meta']['msg']))
        namespace.blogname = value


class ArgParser(argparse.ArgumentParser):

    def __init__(self, config=None, **kwargs):
        super().__init__(add_help=False, **kwargs)
        self.namespace = argparse.Namespace()
        self.namespace.config = config

    def error(self, message):
        raise ArgumentException(message)

    def exit(self, status=0, message=None):
        if message is None:
            message = "argparse exited with status %d." % status
        raise ArgumentException(message)

    def parse_args(self, msg):
        return super().parse_args(msg.split(), namespace=self.namespace)

    def parse_known_args(self, msg, namespace=None):
        args = msg.split() if isinstance(msg, str) else msg
        namespace = self.namespace if namespace is None else namespace
        return super().parse_known_args(args, namespace)
