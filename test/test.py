#!/usr/bin/env python3
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import configparser
import logging
import shutil
import socket
import sys
import tempfile
import unittest
from os.path import dirname, exists, join
from unittest import mock


# Make this work from git.
if exists(join(dirname(__file__), '../.git')):
    sys.path.insert(0, join(dirname(__file__), '..'))

# Imports pkg_resources, so must come after the path is modified
import irc.client  # noqa
from cslbot.helpers import core, workers  # noqa

# We don't need the alembic output.
logging.getLogger("alembic").setLevel(logging.WARNING)


def connect_mock(conn, *args, **_):
    conn.real_nickname = 'testBot'
    conn.handlers = {}
    conn.socket = mock.Mock()


def start_thread(self, func, *args, **kwargs):
    # We need to actually run the server thread to avoid blocking.
    if hasattr(func, '__func__') and func.__func__.__name__ == 'serve_forever':
        with self.worker_lock:
            self.executor.submit(func, *args, **kwargs)
    else:
        func(*args, **kwargs)


# TODO: break this up more
class BotTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.confdir = tempfile.TemporaryDirectory()
        srcdir = join(dirname(__file__), '..', 'cslbot', 'static')
        config_file = join(cls.confdir.name, 'config.cfg')
        shutil.copy(join(srcdir, 'config.example'), config_file)
        shutil.copy(join(srcdir, 'groups.example'), join(cls.confdir.name, 'groups.cfg'))
        config_obj = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        with open(config_file) as f:
                config_obj.read_file(f)

        # Prevent server port conflicts
        config_obj['core']['serverport'] = str(config_obj.getint('core', 'serverport') + 1000)
        # Use an in-memory sqlite db for testing
        config_obj['db']['engine'] = 'sqlite://'

        with open(config_file, 'w') as f:
                config_obj.write(f)

    @classmethod
    def tearDownClass(cls):
        cls.confdir.cleanup()

    def setUp(self):
        mock.patch.object(irc.client.ServerConnection, 'connect', connect_mock).start()
        self.bot = core.IrcBot(self.confdir.name)
        self.setup_handler()
        # We don't actually connect to an irc server, so fake the event loop
        with mock.patch.object(irc.client.Reactor, 'process_forever'):
            self.bot.start()
        self.join_channel('testBot', '#test-channel')

    def setup_handler(self):
        self.log_mock = mock.patch.object(self.bot.handler.db, 'log').start()
        mock.patch.object(workers.Workers, 'start_thread', start_thread).start()

    def tearDown(self):
        self.bot.shutdown_mp()

    def join_channel(self, nick, channel):
        e = irc.client.Event('join', irc.client.NickMask(nick), channel)
        calls = self.send_msg(e)
        expected_calls = [(nick, channel, 0, '', 'join')]
        if nick == 'testBot':
            expected_calls.append((nick, 'private', 0, 'Joined channel %s' % channel, 'privmsg'))
        self.assertEqual(calls, expected_calls)
        self.log_mock.reset_mock()

    def send_msg(self, e):
        # We mocked out the actual irc processing, so call the internal method here.
        self.bot.connection._handle_event(e)
        # Make hermetic
        return sorted([x[0] for x in self.log_mock.call_args_list])

    def test_handle_msg(self):
        """Make sure the bot can handle a simple message."""
        e = irc.client.Event('pubmsg', irc.client.NickMask('testnick'), '#test-channel', ['!morse bob'])
        calls = self.send_msg(e)
        self.assertEqual(calls, [('testBot', '#test-channel', 0, '-... --- -...', 'privmsg'), ('testnick', '#test-channel', 0, '!morse bob', 'pubmsg')])

    def test_handle_nick(self):
        """Test the bot's ability to handle nick change events"""
        # Hack: since we don't have a real IRC connection, we must manually "join" the nicks
        self.join_channel('testBot', '#test-channel2')
        self.join_channel('testnick', '#test-channel')
        self.join_channel('testnick', '#test-channel2')
        e = irc.client.Event('nick', irc.client.NickMask('testnick'), 'testnick2')
        calls = self.send_msg(e)
        self.assertEqual(calls, [('testnick', '#test-channel', 0, 'testnick2', 'nick'), ('testnick', '#test-channel2', 0, 'testnick2', 'nick')])

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

    # Command-specific messages
    @mock.patch('cslbot.commands.zipcode.get')
    def test_zipcode_valid(self, mock_get):
        """Test a correct zip code"""
        with open(join(dirname(__file__), 'data', 'zipcode_12345.xml')) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())
        e = irc.client.Event('pubmsg', irc.client.NickMask('testnick'), '#test-channel', ['!zipcode 12345'])
        calls = self.send_msg(e)
        self.assertEqual(calls, [('testBot', '#test-channel', 0, '12345: Schenectady, NY', 'privmsg'), ('testnick', '#test-channel', 0, '!zipcode 12345', 'pubmsg')])

    def test_zipcode_invalid(self):
        """Test incorrect zip codes"""
        e = irc.client.Event('pubmsg', irc.client.NickMask('testnick'), '#test-channel', ['!zipcode potato'])
        calls = self.send_msg(e)
        self.assertEqual(calls, [('testBot', '#test-channel', 0, "Couldn't parse a ZIP code from potato", 'privmsg'), ('testnick', '#test-channel', 0, '!zipcode potato', 'pubmsg')])

    @mock.patch('cslbot.commands.define.get')
    def test_definition_valid(self, mock_get):
        """Test a valid definition"""
        with open(join(dirname(__file__), 'data', 'define_potato.xml')) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())
        e = irc.client.Event('pubmsg', irc.client.NickMask('testnick'), '#test-channel', ['!define potato'])
        calls = self.send_msg(e)
        self.assertEqual(calls,
                         [('testBot', '#test-channel', 0, 'potato, white potato, Irish potato, murphy, spud, tater: an edible tuber native to South America; a staple food of Ireland', 'privmsg'),
                          ('testnick', '#test-channel', 0, '!define potato', 'pubmsg')])

    @mock.patch('cslbot.commands.define.get')
    def test_definition_invalid(self, mock_get):
        """Test an invalid definition"""
        with open(join(dirname(__file__), 'data', 'define_potatwo.xml')) as test_data_file:
            mock_get.return_value = mock.Mock(content=test_data_file.read().encode())
        e = irc.client.Event('pubmsg', irc.client.NickMask('testnick'), '#test-channel', ['!define potatwo'])
        calls = self.send_msg(e)
        self.assertEqual(calls, [('testBot', '#test-channel', 0, 'No results found for potatwo', 'privmsg'), ('testnick', '#test-channel', 0, '!define potatwo', 'pubmsg')])

if __name__ == '__main__':
    loglevel = logging.DEBUG if '-v' in sys.argv else logging.INFO
    logging.basicConfig(level=loglevel)
    unittest.main()
