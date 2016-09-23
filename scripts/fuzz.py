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
import socketserver
import threading
from os.path import dirname, exists, join
from sys import path, stdin
from unittest import mock

import afl

# Make this work from git.
if exists(join(dirname(__file__), '../.git')):
    path.insert(0, join(dirname(__file__), '..'))

# Imports pkg_resources, so must come after the path is modified
import irc.client  # noqa
from cslbot.helpers import core, server, workers  # noqa


def connect_mock(conn, *args, **_):
    conn.real_nickname = 'testBot'
    conn.handlers = {}
    conn.socket = mock.MagicMock()


class ThreadMock():
    name = 'Thread-7'


def setup_mocks() -> None:
    mock.patch.object(irc.client.ServerConnection, 'connect', connect_mock).start()
    mock.patch.object(socketserver.TCPServer, 'server_bind').start()
    mock.patch.object(socketserver.TCPServer, 'serve_forever').start()
    mock.patch('socketserver.ThreadingMixIn').start()
    mock.patch('multiprocessing.Pool').start()
    mock.patch('concurrent.futures.ThreadPoolExecutor').start()
    mock.patch.object(threading, 'current_thread', ThreadMock).start()
    mock.patch.object(workers.Workers, 'start_thread', lambda _, func, *args, **kwargs: func(*args, **kwargs)).start()
    mock.patch.object(workers.Workers, 'run_pool', new=lambda func, *args: func(*args)).start()
    mock.patch.object(workers.Workers, 'defer').start()


def setup_bot() -> core.IrcBot:
    confdir = join(dirname(__file__), '..')
    bot = core.IrcBot(confdir)
    mock.patch.dict(bot.handler, 'channels', {'#test-channel': mock.MagicMock()}).start()
    mock.patch.object(bot.handler, 'is_ignored', return_value=False).start()
    mock.patch.object(bot.handler,'db').start()
    # We don't actually connect to an irc server, so fake the event loop
    with mock.patch.object(irc.client.Reactor, 'process_forever'):
        bot.start()
    return bot


setup_mocks()
bot = setup_bot()
e = irc.client.Event('privmsg', irc.client.NickMask('dankmemes'), '#test-channel')
while afl.loop(5):
    try:
        e.arguments = [stdin.readline()]
    except UnicodeDecodeError:
        continue
    bot.handler.handle_msg(bot.connection, e)
