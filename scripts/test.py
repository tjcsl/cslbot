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

import unittest
from unittest import mock
from os.path import dirname, join
import configparser
import importlib
import sys
import irc.client

# FIXME: sibling imports
sys.path.append(dirname(__file__) + '/..')


class BotTest(unittest.TestCase):

    @mock.patch('socket.socket')
    @mock.patch.object(irc.client.Reactor, 'process_forever')
    def test_bot_init(self, *args):
        """Make sure the bot starts up correctly."""
        bot_mod = importlib.import_module('bot')
        botconfig = configparser.ConfigParser()
        configfile = join(dirname(__file__), '../config.cfg')
        with open(configfile) as conf:
            botconfig.read_file(conf)
        bot = bot_mod.IrcBot(botconfig)
        bot.start()
        bot.shutdown_workers()

if __name__ == '__main__':
    unittest.main()
