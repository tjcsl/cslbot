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
import configparser
import logging
import importlib
import multiprocessing
import queue
import ssl
import threading
import traceback
from os import path
from irc import bot, connection
from . import backtrace, config, handler, misc, reloader, server


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
        self.event_queue = queue.Queue()
        # Are we running in bare-bones, reload-only mode?
        self.reload_event = threading.Event()
        # fix unicode problems
        self.connection.buffer_class.errors = 'replace'

        if not reloader.load_modules(botconfig):
            raise Exception("Failed to load modules.")

        self.handler = handler.BotHandler(botconfig, self.connection, self.channels)
        if botconfig['feature'].getboolean('server'):
            self.server = server.init_server(self)

    def handle_event(self, c, e):
        handled_types = ['action', 'authenticate', 'bannedfromchan', 'cap', 'ctcpreply', 'error', 'join', 'kick',
                         'mode', 'nicknameinuse', 'nosuchnick', 'nick', 'part', 'privmsg', 'privnotice', 'pubnotice', 'pubmsg', 'welcome']
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

    def get_version(self):
        """Get the version."""
        _, version = misc.get_version()
        if version is None:
            return "Can't get the version."
        else:
            return "cslbot - %s" % version

    def do_sasl(self, _):
        self.connection.cap('REQ', 'sasl')

    @staticmethod
    def get_target(e):
        if e.target[0] in ['#', '&', '+', '!']:
            return e.target
        else:
            return e.source.nick

    def shutdown_mp(self, clean=True):
        """ Shutdown all the multiprocessing.

        :param bool clean: Whether to shutdown things cleanly, or force a quick and dirty shutdown.
        """
        # The server runs on a worker thread, so we need to shut it down first.
        if hasattr(self, 'server'):
            self.server.socket.close()
            self.server.shutdown()
        if hasattr(self, 'handler'):
            self.handler.workers.stop_workers(clean)

    def handle_quit(self, _, e):
        # Log quits.
        for channel in misc.get_channels(self.channels, e.source.nick):
            self.handler.do_log(channel, e.source, e.arguments[0], 'quit')
        # If we're the one quiting, shut things down cleanly.
        if e.source.nick == self.connection.real_nickname:
            # FIXME: If this hangs or takes more then 5 seconds, we'll just reconnect.
            self.shutdown_mp()
            sys.exit(0)

    def handle_msg(self, c, e):
        """Handles all messages.

        | If a exception is thrown, catch it and display a nice traceback instead of crashing.
        | Do the appropriate processing for each event type.
        """
        try:
            self.handler.handle_msg(c, e)
        except Exception as ex:
            backtrace.handle_traceback(ex, c, self.get_target(e), self.config)

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


def init(confdir=None):
    """The bot's main entry point.

    | Initialize the bot and start processing messages.
    """
    multiprocessing.set_start_method('spawn')

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debug logging.', action='store_true')
    args = parser.parse_args()
    loglevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=loglevel)

    confdir = confdir if confdir is not None else "/etc/cslbot"
    config_file = path.join(confdir, 'config.cfg')
    if not path.exists(config_file):
        logging.info("Setting up config file")
        config.do_setup(config_file)
        return
    botconfig = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
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
    except Exception as ex:
        bot.shutdown_mp(False)
        logging.error("The bot died! %s" % ex)
        output = "".join(traceback.format_exc())
        for line in output.split('\n'):
            logging.error(line)
        sys.exit(1)
