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

import threading
import unittest
from unittest import mock
import configparser
import socket
import irc.client
from cslbot.helpers import core, server


class BotTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        confdir = join(dirname(__file__), '..')
        mock.patch.object(configparser.ConfigParser, 'getint', cls.config_mock).start()
        cls.bot = core.IrcBot(confdir)
        cls.setup_handler()
        # We don't actually connect to an irc server, so fake the event loop
        with mock.patch.object(irc.client.Reactor, 'process_forever'):
            cls.bot.start()

    @classmethod
    def tearDownClass(cls):
        cls.bot.shutdown_mp()

    @classmethod
    def setup_handler(cls):
        cls.bot.handler.connection = mock.MagicMock(real_nickname='testBot')
        cls.bot.handler.channels = {'#test-channel': mock.MagicMock()}
        cls.bot.handler.is_ignored = mock.MagicMock(return_value=False)
        cls.bot.handler.db = mock.MagicMock()

    @staticmethod
    def config_mock(config, section, option):
        ret = int(config[section][option])
        # Avoid port conflicts with running bot
        if section == 'core' and option == 'serverport':
            return ret + 1000
        return ret

    def restart_workers(self):
        """Force all the workers to restart so we get the log message."""
        self.bot.shutdown_mp()
        self.bot.handler.workers.__init__(self.bot.handler)
        self.bot.server = server.init_server(self.bot)

    def do_reload(self):
        sock = socket.socket()
        port = self.bot.config.getint('core', 'serverport')
        passwd = self.bot.config['auth']['ctrlpass']
        sock.connect(('localhost', port))
        msg = '%s\nreload' % passwd
        sock.send(msg.encode())
        output = []
        while len(output) < 3:
            resp = sock.recv(4096)
            output.append(resp)
        sock.close()
        self.reload_output = "".join([x.decode() for x in output])

    def test_handle_msg(self):
        """Make sure the bot can handle a simple message."""
        e = irc.client.Event('pubmsg', irc.client.NickMask('testnick'), '#test-channel', ['!morse bob'])
        # We mocked out the actual irc processing, so call the internal method here.
        self.bot.connection._handle_event(e)
        self.restart_workers()
        calls = [x[0] for x in self.bot.handler.db.log.call_args_list]
        self.assertEqual(calls, [('testnick', '#test-channel', 0, '!morse bob', 'pubmsg'), ('testBot', '#test-channel', 0, '-... --- -...', 'privmsg')])

    def test_bot_reload(self):
        """Make sure the bot can reload without errors."""
        # We need to run this in a seperate thread for it to work correctly.
        thread = threading.Thread(target=self.do_reload)
        thread.start()
        # FIXME: sometimes this hangs, not clear why.
        thread.join()
        self.setup_handler()
        self.assertEqual(self.reload_output, "Password: \nAye Aye Capt'n\n")

if __name__ == '__main__':
    unittest.main()
