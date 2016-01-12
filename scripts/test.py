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
import configparser
import socket
import logging
import unittest
from unittest import mock
# Make this work from git.
if exists(join(dirname(__file__), '../.git')):
    path.insert(0, join(dirname(__file__), '..'))

# Imports pkg_resources, so must come after the path is modified
import irc.client  # noqa
from cslbot.helpers import core, server  # noqa


def config_mock(config, section, option):
    ret = int(config[section][option])
    # Avoid port conflicts with running bot
    if section == 'core' and option == 'serverport':
        return ret + 1000
    return ret


def connect_mock(conn, *args, **_):
    conn.real_nickname = 'testBot'
    conn.handlers = {}
    conn.socket = mock.MagicMock()


class BotTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        confdir = join(dirname(__file__), '..')
        mock.patch.object(configparser.ConfigParser, 'getint', config_mock).start()
        mock.patch.object(irc.client.ServerConnection, 'connect', connect_mock).start()
        # FIXME: don't request oauth tokens
        # mock.patch('cslbot.helpers.tokens.update_all_tokens').start()
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
        cls.bot.handler.channels = {'#test-channel': mock.MagicMock()}
        cls.bot.handler.is_ignored = mock.MagicMock(return_value=False)
        cls.bot.handler.db = mock.MagicMock()

    def restart_workers(self):
        """Force all the workers to restart so we get the log message."""
        self.bot.shutdown_mp()
        self.bot.handler.workers.__init__(self.bot.handler)
        self.bot.server = server.init_server(self.bot)

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
        sock = socket.socket()
        port = self.bot.config.getint('core', 'serverport')
        passwd = self.bot.config['auth']['ctrlpass']
        sock.connect(('localhost', port))
        msg = '%s\nreload' % passwd
        sock.send(msg.encode())
        output = "".encode()
        while len(output) < 20:
            output += sock.recv(4096)
        sock.close()
        self.setup_handler()
        self.assertEqual(output.decode(), "Password: \nAye Aye Capt'n\n")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
