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
import concurrent.futures
import configparser
import logging
import random
import re
import shutil
import tempfile
import unittest
from os.path import dirname, join
from unittest import mock

import irc.client

from cslbot.helpers import core, handler, workers


def start_thread(self, func, *args, **kwargs):
    # We need to actually run the server thread to avoid blocking.
    if hasattr(func, '__func__') and func.__func__.__name__ == 'serve_forever':
        with self.worker_lock:
            self.executor.submit(func, *args, **kwargs)
    else:
        f = concurrent.futures.Future()
        f.set_result(func(*args, **kwargs))
        return f


def rate_limited_send(self, mtype, target, msg=None):
    getattr(self.connection, mtype)(target, msg)


class BotTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cap_done = False
        cls.user_done = False
        cls.cap_list = []
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
        config_obj['db']['sqlalchemy.url'] = 'sqlite://'

        # Setup some default values.
        config_obj['core']['nick'] = 'testBot'
        config_obj['core']['host'] = 'irc.does.not.exist'
        config_obj['core']['channel'] = '#test-channel'
        config_obj['core']['ctrlchan'] = '#test-control'
        config_obj['core']['sasl'] = 'True'
        config_obj['auth']['serverpass'] = 'dankmemes'
        cls.config_obj = config_obj

        with open(config_file, 'w') as f:
            config_obj.write(f)

    @classmethod
    def tearDownClass(cls):
        cls.confdir.cleanup()

    def join_mock(self, channel, key=None):
        # Since we don't have a real server on the other end, we need to fake a JOIN reply.
        self.send_msg('join', self.nick, channel)

    def who_mock(self, target, op=None):
        # Since we don't have a real server on the other end, we need to fake a WHOSPCRPL.
        nick, tag = re.match(r'(#?[\w-]+) %naft,(\d+)', target).groups()
        self.send_msg('whospcrpl', self.server, self.nick, [tag, nick, 'H', nick])

    def cap_mock(self, cmd, arg=None):
        if cmd == 'END':
            self.cap_done = True
        elif self.cap_done:
            raise Exception(f'{cmd} {arg} sent after CAP END')
        elif cmd == 'REQ' and arg is not None:
            self.cap_list.append(arg)
        else:
            raise Exception(f"Unhandled CAP {cmd} {arg}")

    def user_mock(self, username, realname):
        self.bot.connection.send_raw(f"USER {username} 0 * :{realname}")
        for cap in self.cap_list:
            self.send_msg('cap', self.server, '*', ['ACK', cap])
        self.cap_list.clear()

    def raw_handler(self, msg):
        logging.debug("TO SERVER: %s", msg)
        msg = msg.split()
        if msg == ['AUTHENTICATE', 'PLAIN']:
            self.send_msg('authenticate', None, '+')

    def setUp(self):
        mock.patch('irc.connection.Factory').start()
        mock.patch.object(irc.client.ServerConnection, 'join', self.join_mock).start()
        mock.patch.object(irc.client.ServerConnection, 'who', self.who_mock).start()
        mock.patch.object(irc.client.ServerConnection, 'cap', self.cap_mock).start()
        mock.patch.object(irc.client.ServerConnection, 'user', self.user_mock).start()
        self.bot = core.IrcBot(self.confdir.name, self.config_obj, ['irc.does.not.exist'], 0)
        self.setup_handler()
        # We don't actually connect to an irc server, so fake the event loop
        self.bot._connect()
        self.do_welcome()

    def tearDown(self):
        self.bot.shutdown_mp()

    def setup_handler(self):
        # We don't need to rate-limit sending.
        mock.patch.object(handler.BotHandler, 'rate_limited_send', rate_limited_send).start()
        # Setup the mock to record log calls.
        self.log_mock = mock.patch.object(self.bot.handler.db, 'log').start()
        self.raw_mock = mock.patch.object(irc.client.ServerConnection, 'send_raw', mock.Mock(wraps=self.raw_handler)).start()
        # Force normally-threaded operations to execute synchronously
        mock.patch.object(workers.Workers, 'start_thread', start_thread).start()

    def join_channel(self, nick, channel):
        calls = self.send_msg('join', nick, channel)
        expected_calls = [(nick, channel, 0, '', 'join', self.server)]
        if nick == self.nick:
            expected_calls.append((nick, self.ctrlchan, 0, 'Joined channel %s' % channel, 'privmsg', self.server))
        self.assertEqual(calls, expected_calls)
        self.log_mock.reset_mock()

    @property
    def nick(self):
        return self.bot.connection.real_nickname

    @property
    def channel(self):
        return self.bot.config['core']['channel']

    @property
    def ctrlchan(self):
        return self.bot.config['core']['ctrlchan']

    @property
    def server(self):
        return self.bot.config['core']['host']

    def do_welcome(self):
        with self.assertLogs('cslbot.helpers.handler') as mock_log:
            calls = self.send_msg('welcome', self.server, self.nick, ['Welcome to TestIRC, %s!' % self.nick])
        self.assertEqual(mock_log.output, ['INFO:cslbot.helpers.handler:Connected to server %s' % self.server])
        self.assertTrue(self.bot.handler.features['account-notify'])
        self.assertTrue(self.bot.handler.features['extended-join'])
        # We support WHOX!
        self.send_msg('featurelist', self.server, self.nick, ['WHOX'])
        self.assertTrue(self.bot.handler.features['whox'])
        expected_calls = [(self.nick, self.channel, 0, '', 'join', self.server), (self.nick, self.ctrlchan, 0, '', 'join', self.server),
                          (self.nick, self.ctrlchan, 0, 'Joined channel %s' % self.ctrlchan, 'privmsg', self.server),
                          (self.nick, 'private', 0, 'Joined channel %s' % self.channel, 'privmsg', self.server)]
        self.assertEqual(calls, expected_calls)
        self.assertEqual(
            sorted(x[0] for x in self.raw_mock.call_args_list),
            [
                ('AUTHENTICATE PLAIN',),
                ('AUTHENTICATE dGVzdEJvdAB0ZXN0Qm90AGRhbmttZW1lcw==',),  # nick=testBot, password=dankmemes
                ('NICK %s' % self.nick,),
                (f'PRIVMSG {self.ctrlchan} :Joined channel {self.channel}',),
                (f'PRIVMSG {self.ctrlchan} :Joined channel {self.ctrlchan}',),
                (f'USER {self.nick} 0 * :{self.nick}',)
            ])
        self.log_mock.reset_mock()

    def send_msg(self, mtype, source, target, arguments=None):
        e = irc.client.Event(mtype, irc.client.NickMask(source), target, arguments or [])
        logging.debug("type: %s, source: %s, target: %s, arguments: %s, tags: %s", e.type, e.source, e.target, e.arguments, e.tags)
        # We mocked out the actual irc processing, so call the internal method here.
        self.bot.connection._handle_event(e)
        # Make hermetic
        return sorted(x[0] for x in self.log_mock.call_args_list)
