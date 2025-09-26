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

import argparse
import functools
import importlib
import logging
import queue
import signal
import socket
import ssl
import sys
import threading
import traceback
from os import path

from irc import bot, client, connection

if sys.version_info < (3, 7):
    # Dependency on importlib.resources
    raise Exception("Need Python 3.7 or higher.")

from . import backtrace, config, handler, misc, orm, reloader, server  # noqa

shutdown = threading.Event()


class IrcBot(bot.SingleServerIRCBot):

    def __init__(self, confdir, config, spec, idx):
        """Setup everything."""
        signal.signal(signal.SIGTERM, self.shutdown)
        self.confdir = confdir
        self.config = config
        self.idx = idx
        if self.config.getboolean('core', 'ssl'):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            factory = connection.Factory(wrapper=ctx.wrap_socket, ipv6=self.config.getboolean('core', 'ipv6'))
        else:
            factory = connection.Factory(ipv6=self.config.getboolean('core', 'ipv6'))
        nick = self.config['core']['nick']
        self.reactor_class = functools.partial(client.Reactor, on_connect=self.do_cap)
        super().__init__([spec], nick, nick, connect_factory=factory)
        # These allow reload events to be processed when a reload has failed.
        self.connection.add_global_handler("pubmsg", self.reload_handler, -30)
        self.connection.add_global_handler("privmsg", self.reload_handler, -30)
        self.connection.add_global_handler("all_events", self.handle_event, 10)
        # We need to get the channels that a nick is currently in before the regular quit event is processed and the nick is removed from self.channels.
        self.connection.add_global_handler("quit", self.handle_quit, -21)
        self.event_queue = queue.Queue()
        # Are we running in bare-bones, reload-only mode?
        self.reload_event = threading.Event()
        # fix unicode problems
        self.connection.buffer_class.errors = 'replace'

        if not reloader.load_modules(self.config, confdir):
            raise Exception("Failed to load modules.")

        self.handler = handler.BotHandler(self.config, self.connection, self.channels, confdir, self.idx)
        if self.config['feature'].getboolean('server'):
            self.server = server.init_server(self)

    def handle_event(self, c, e):
        handled_types = [
            'account', 'action', 'authenticate', 'bannedfromchan', 'cap', 'ctcpreply', 'error', 'featurelist', 'join', 'kick', 'mode',
            'nicknameinuse', 'nosuchnick', 'nick', 'part', 'privmsg', 'privnotice', 'pubnotice', 'pubmsg', 'topic', 'welcome', 'whospcrpl'
        ]
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
        _, version = misc.get_version(self.confdir)
        if version is None:
            return "Can't get the version."
        else:
            return "cslbot - %s" % version

    def do_cap(self, _):
        self.connection.cap('REQ', 'account-notify')
        self.connection.cap('REQ', 'extended-join')
        if self.config.getboolean('core', 'sasl'):
            self.connection.cap('REQ', 'sasl')
        else:
            self.connection.cap('END')

    def start(self):
        self._connect()
        # Set our name.
        threading.current_thread().name = '%s message loop' % self.connection.server
        while not shutdown.is_set():
            self.reactor.process_once(timeout=0.2)
        self.shutdown_mp()
        self.connection.close()

    @staticmethod
    def get_target(e):
        if e.target[0] in ['#', '&', '+', '!']:
            return e.target
        else:
            return e.source.nick

    def shutdown(self, *_):
        if hasattr(self, 'connection'):
            self.connection.disconnect("Bot received SIGTERM")
        shutdown.set()

    def shutdown_mp(self, clean=True):
        """Shutdown all the multiprocessing.

        :param bool clean: Whether to shutdown things cleanly, or force a quick and dirty shutdown.

        """
        # The server runs on a worker thread, so we need to shut it down first.
        if hasattr(self, 'server'):
            # Shutdown the server quickly.
            try:
                # For some strange reason, this throws an OSError on windows.
                self.server.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.server.socket.close()
            self.server.shutdown()
        if hasattr(self, 'handler'):
            self.handler.workers.stop_workers(clean)

    def handle_quit(self, _, e):
        # Log quits.
        for channel in misc.get_channels(self.channels, e.source.nick):
            self.handler.do_log(channel, e.source, e.arguments[0], 'quit')
        # If we're the one quiting, shut things down cleanly.
        # If it's an Excess Flood or other server-side quit we want to reconnect.
        if e.source.nick == self.connection.real_nickname and e.arguments[0] in ['Client Quit', 'Quit: Goodbye, Cruel World!']:
            print("shutdown")
            shutdown.set()

    def handle_msg(self, c, e):
        """Handles all messages.

        - If a exception is thrown, catch it and display a nice traceback instead of crashing.
        - Do the appropriate processing for each event type.

        """
        try:
            self.handler.handle_msg(c, e)
        except Exception as ex:
            backtrace.handle_traceback(ex, c, self.get_target(e), self.config)

    def is_reload(self, e):
        if not e.arguments:
            return None
        cmd = e.arguments[0].strip()
        if not cmd:
            return None
        cmd = misc.get_cmdchar(self.config, self.connection, cmd, e.type)
        cmdchar = self.config['core']['cmdchar']
        if cmd.startswith('%sreload' % cmdchar):
            return cmd
        else:
            return None

    def reload_handler(self, c, e):
        """This handles reloads."""
        cmd = self.is_reload(e)
        cmdchar = self.config['core']['cmdchar']
        if cmd is not None:
            # If we're in a minimal reload state, only the owner can do stuff, as we can't rely on the db working.
            if self.reload_event.set():
                admins = [self.config['auth']['owner']]
            else:
                with self.handler.db.session_scope() as session:
                    admins = [x.nick for x in session.query(orm.Permissions).all()]
            if e.source.nick not in admins:
                c.privmsg(self.get_target(e), "Nope, not gonna do it.")
                return
            importlib.reload(reloader)
            self.reload_event.set()
            cmdargs = cmd[len('%sreload' % cmdchar) + 1:]
            try:
                if reloader.do_reload(self, e, cmdargs):
                    if self.config.getboolean('feature', 'server'):
                        self.server = server.init_server(self)
                    self.reload_event.clear()
                logging.info("Successfully reloaded %s", self.connection.server)
            except Exception as ex:
                backtrace.handle_traceback(ex, c, self.get_target(e), self.config)


def init(confdir="/etc/cslbot"):
    """The bot's main entry point.

    | Initialize the bot and start processing messages.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debug logging.', action='store_true')
    parser.add_argument('--validate', help='Initialize the db and perform other sanity checks.', action='store_true')
    args = parser.parse_args()
    loglevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=loglevel, format="%(asctime)s %(levelname)s:%(module)s:%(message)s")
    # We don't need a bunch of output from the requests module.
    logging.getLogger("requests").setLevel(logging.WARNING)

    config_file = path.join(confdir, 'config.cfg')
    if not path.exists(config_file):
        logging.info("Setting up config file")
        config.do_setup(config_file)
        sys.exit(0)

    cfg = config.load_config(config_file, logging.info)
    bots = []
    for idx, host in enumerate(cfg['core']['host'].split(',')):
        if cfg.getboolean('core', 'sasl'):
            passwd = None
        else:
            passwd = cfg['auth']['serverpass'].split(',')[idx].strip()
        spec = bot.ServerSpec(host.strip(), cfg.getint('core', 'ircport'), passwd)
        cslbot = IrcBot(confdir, cfg, spec, idx)
        bots.append(cslbot)

    if args.validate:
        for cslbot in bots:
            cslbot.shutdown_mp()
        print("Everything is ready to go!")
        return

    threads = []
    try:
        for cslbot in bots:
            t = threading.Thread(target=cslbot.start)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        # KeyboardInterrupt means someone tried to ^C, so shut down the bot
        cslbot.disconnect('Bot received a Ctrl-C')
        shutdown.set()
        for t in threads:
            t.join()
        sys.exit(0)
    except Exception as ex:
        cslbot.disconnect('Bot died.')
        cslbot.shutdown_mp(False)
        logging.error("The bot died! %s", ex)
        output = "".join(traceback.format_exc()).strip()
        for line in output.split('\n'):
            logging.error(line)
        shutdown.set()
        for t in threads:
            t.join()
        sys.exit(1)
