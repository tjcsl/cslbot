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

import sys
if sys.version_info < (3, 4):
    # Dependency on importlib.reload
    raise Exception("Need Python 3.4 or higher.")
import argparse
import base64
import configparser
import logging
import importlib
import multiprocessing
import queue
import random
import ssl
import threading
import time
import traceback
from os import path
from irc import bot, connection
from helpers import backtrace, config, handler, misc, reloader, server


class IrcBot(bot.SingleServerIRCBot):
    def __init__(self, botconfig):
        """Setup everything."""
        if botconfig.getboolean('core', 'ssl'):
            factory = connection.Factory(wrapper=ssl.wrap_socket, ipv6=botconfig.getboolean('core', 'ipv6'))
        else:
            factory = connection.Factory(ipv6=botconfig.getboolean('core', 'ipv6'))
        passwd = None if botconfig.getboolean('core', 'sasl') else botconfig['auth']['serverpass']
        serverinfo = bot.ServerSpec(botconfig['core']['host'], botconfig.getint('core', 'ircport'), passwd)
        nick = botconfig['core']['nick']
        super().__init__([serverinfo], nick, nick, connect_factory=factory, reconnection_interval=5)
        # This does the magic when everything else is dead
        self.connection.add_global_handler("pubmsg", self.reload_handler, -30)
        self.connection.add_global_handler("all_events", self.handle_event, 10)
        # We need to get the channels that a nick is currently in before the regular quit event is processed.
        self.connection.add_global_handler("quit", self.handle_quit, -21)
        if passwd is None:
            # FIXME: make this less hacky
            self.reactor._on_connect = self.do_sasl
        self.config = botconfig
        self.handler = handler.BotHandler(botconfig)
        if not reloader.load_modules(botconfig):
            # The initial load of commands/hooks failed, so bail out.
            sys.exit(1)
        self.event_queue = queue.Queue()
        # Are we running in bare-bones, reload-only mode?
        self.reload_event = threading.Event()

        if botconfig['feature'].getboolean('server'):
            self.server = server.init_server(self)
        # fix unicode problems
        self.connection.buffer_class.errors = 'replace'

    def handle_event(self, c, e):
        handled_types = ['903', 'action', 'authenticate', 'bannedfromchan', 'cap', 'ctcpreply', 'error', 'join', 'kick',
                         'mode', 'nicknameinuse', 'nick', 'part', 'privmsg', 'privnotice', 'pubnotice', 'pubmsg', 'quit', 'welcome']
        # We only need to do stuff for a sub-set of events.
        if e.type not in handled_types:
            return
        if self.reload_event.is_set():
            # Don't queue up failed reloads.
            if self.is_reload(e) is None:
                self.event_queue.put(e)
        else:
            # Handle any queued events first.
            while not self.event_queue.empty():
                self.handle_msg(c, self.event_queue.get_nowait())
            self.handle_msg(c, e)

    @staticmethod
    def get_version():
        """Get the version."""
        # FIXME: don't hard-code
        return "cslbot - v0.9"

    def do_sasl(self, _):
        self.connection.cap('REQ', 'sasl')

    @staticmethod
    def get_target(e):
        if e.target[0] == '#' or e.target[0] == '@' or e.target[0] == '+':
            return e.target
        else:
            return e.source.nick

    def shutdown_server(self):
        if hasattr(self, 'server'):
            self.server.socket.close()
            self.server.shutdown()

    def shutdown_workers(self, clean):
        if hasattr(self, 'handler'):
            self.handler.workers.stop_workers(clean)

    def shutdown_mp(self, clean=True):
        """ Shutdown all the multiprocessing.

        :param bool clean: Whether to shutdown things cleanly, or force a quick and dirty shutdown.
        """
        self.shutdown_server()
        self.shutdown_workers(clean)

    def do_rejoin(self, c, e):
        if e.arguments[0] in self.channels:
            return
        # If we're still banned, this will trigger a bannedfromchan event so we'll try again.
        c.join(e.arguments[0])

    def handle_quit(self, _, e):
        # Log quits.
        for channel in misc.get_channels(self.channels, e.source.nick):
            self.handler.do_log(channel, e.source, e.arguments[0], 'quit')

    def handle_msg(self, c, e):
        """Handles all messages.

        | If a exception is thrown, catch it and display a nice traceback instead of crashing.
        | Do the appropriate processing for each event type.
        """
        if e.type in ['pubmsg', 'privmsg', 'action', 'privnotice', 'pubnotice', 'mode', 'join', 'part', 'kick']:
            try:
                self.handler.handle_msg(e.type, c, e)
            except Exception as ex:
                backtrace.handle_traceback(ex, c, self.get_target(e), self.config)
        elif e.type == '903':
            # The SASL Successful event doesn't have a pretty name.
            if e.arguments[0] == 'SASL authentication successful':
                self.connection.cap('END')
        elif e.type == 'cap':
            if 'ACK sasl' == ' '.join(e.arguments).strip():
                self.connection.send_raw('AUTHENTICATE PLAIN')
        elif e.type == 'authenticate':
            if e.target == '+':
                passwd = self.config['auth']['serverpass']
                user = self.config['core']['nick']
                token = base64.b64encode('\0'.join([user, user, passwd]).encode())
                self.connection.send_raw('AUTHENTICATE %s' % token.decode())
        elif e.type == 'nicknameinuse':
            self.connection.nick('Guest%d' % random.getrandbits(20))
            self.connection.privmsg('NickServ', 'REGAIN %s %s' % (self.config['core']['nick'], self.config['auth']['serverpass']))
            self.handler.workers.defer(5, False, self.do_welcome, c)
        elif e.type == 'welcome':
            logging.info("Connected to server %s", self.config['core']['host'])
            self.handler.do_welcome(self)
        elif e.type == 'nick':
            # Log nick changes.
            for channel in misc.get_channels(self.channels, e.target):
                self.handler.do_log(channel, e.source.nick, e.target, 'nick')
            self.handler.handle_msg('nick', c, e)
        elif e.type == 'bannedfromchan':
            self.handler.workers.defer(5, False, self.do_rejoin, c, e)
        elif e.type == 'ctcpreply':
            # FIXME: make this less hacky.
            if len(e.arguments) == 2:
                misc.ping(c, e, time.time())
        elif e.type == 'error':
            logging.error(e.target)
        elif e.type == 'quit':
            # If we're the one quiting, shut things down cleanly.
            if e.source.nick == self.connection.real_nickname:
                # FIXME: If this hangs or takes more then 5 seconds, we'll just reconnect.
                self.shutdown_mp()
                sys.exit(0)
        else:
            raise Exception('Un-handled event type %s' % e.type)

    def is_reload(self, e):
        cmd = e.arguments[0].strip()
        if not cmd:
            return None
        cmd = misc.get_cmdchar(self.config, self.connection, cmd, e.type)
        cmdchar = self.config['core']['cmdchar']
        if cmd.split()[0] == '%sreload' % cmdchar:
            return cmd
        else:
            return None

    def reload_handler(self, c, e):
        """This handles reloads."""
        if e.type not in ['pubmsg', 'privmsg']:
            return
        cmd = self.is_reload(e)
        cmdchar = self.config['core']['cmdchar']
        if cmd is not None:
            admins = [x.strip() for x in self.config['auth']['admins'].split(',')]
            if e.source.nick not in admins:
                c.privmsg(self.get_target(e), "Nope, not gonna do it.")
                return
            importlib.reload(reloader)
            self.reload_event.set()
            cmdargs = cmd[len('%sreload' % cmdchar) + 1:]
            if reloader.do_reload(self, self.get_target(e), cmdargs):
                if self.config['feature'].getboolean('server'):
                    self.server = server.init_server(self)
                self.reload_event.clear()


def main():
    """The bot's main entry point.

    | Initialize the bot and start processing messages.
    """
    config_file = path.join(path.dirname(__file__), 'config.cfg')
    if not path.exists(config_file):
        logging.info("Setting up config file")
        config.do_setup(config_file)
        return
    botconfig = configparser.ConfigParser()
    with open(config_file) as f:
        botconfig.read_file(f)
    bot = IrcBot(botconfig)
    try:
        bot.start()
    except KeyboardInterrupt:
        # KeyboardInterrupt means someone tried to ^C, so shut down the bot
        bot.disconnect('Bot received a Ctrl-C')
        bot.shutdown_mp()
        sys.exit(0)
    except Exception as e:
        bot.shutdown_mp(False)
        logging.error("The bot died! %s" % e)
        output = "".join(traceback.format_exc())
        for line in output.split('\n'):
            logging.error(line)
        sys.exit(1)

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debug logging.', action='store_true')
    args = parser.parse_args()
    loglevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=loglevel)
    main()
