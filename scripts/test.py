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
import socket
import irc.client

# FIXME: sibling imports
sys.path.append(dirname(__file__) + '/..')


@mock.patch.object(irc.client.Reactor, 'process_forever')
class BotTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bot_mod = importlib.import_module('bot')
        botconfig = configparser.ConfigParser()
        configfile = join(dirname(__file__), '../config.cfg')
        with open(configfile) as conf:
            botconfig.read_file(conf)
        port = botconfig.getint('core', 'serverport')
        # Avoid port conflicts with running bot
        botconfig['core']['serverport'] = str(port + 1000)
        cls.bot = bot_mod.IrcBot(botconfig)

    @classmethod
    def tearDownClass(cls):
        cls.bot.shutdown_server()
        cls.bot.shutdown_workers()

    def test_bot_init(self, *args):
        """Make sure the bot starts up correctly."""
        self.bot.start()
        # FIXME: run some commands or something?

    def test_bot_reload(self, *args):
        return
        # FIXME: this needs to run in a seperate thread to work.
        self.bot.reload_event.wait()
        sock = socket.socket()
        port = self.bot.config.getint('core', 'serverport')
        passwd = self.bot.config['auth']['serverpass']
        sock.connect(('localhost', port))
        msg = '%s\nreload' % passwd
        sock.send(msg.encode())
        output = []
        while len(output) < 2:
            resp = sock.recv(4096)
            output.append(resp)
        sock.close()
        output = "".join([x.decode() for x in output])
        self.assertEqual(output, 'Aye')

if __name__ == '__main__':
    unittest.main()
