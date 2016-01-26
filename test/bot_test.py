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
import random
import shutil
import tempfile
import unittest
from os.path import dirname, join
from unittest import mock

from cslbot.helpers import core, handler, workers

import irc.client

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


def rate_limited_send(self, mtype, target, msg):
    getattr(self.connection, mtype)(target, msg)


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
        config_obj['core']['serverport'] = str(config_obj.getint('core', 'serverport') + random.randint(1000, 2000))
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

    def tearDown(self):
        self.bot.shutdown_mp()

    def setup_handler(self):
        # We don't need to rate-limit sending.
        mock.patch.object(handler.BotHandler, 'rate_limited_send', rate_limited_send).start()
        self.log_mock = mock.patch.object(self.bot.handler.db, 'log').start()
        mock.patch.object(workers.Workers, 'start_thread', start_thread).start()

    def join_channel(self, nick, channel):
        calls = self.send_msg('join', nick, channel)
        expected_calls = [(nick, channel, 0, '', 'join')]
        if nick == 'testBot':
            expected_calls.append((nick, 'private', 0, 'Joined channel %s' % channel, 'privmsg'))
        self.assertEqual(calls, expected_calls)
        self.log_mock.reset_mock()

    def send_msg(self, mtype, nick, target, arguments=[]):
        e = irc.client.Event(mtype, irc.client.NickMask(nick), target, arguments)
        # We mocked out the actual irc processing, so call the internal method here.
        self.bot.connection._handle_event(e)
        # Make hermetic
        return sorted([x[0] for x in self.log_mock.call_args_list])
