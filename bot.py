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

try:
    import sys
    if sys.version_info < (3, 4):
        # Dependency on importlib.reload
        raise Exception("Need Python 3.4 or higher.")
    import logging
    import base64
    import argparse
    import ssl
    import time
    import threading
    import random
    import multiprocessing
    import handler
    from helpers import server
    from helpers import config
    from helpers import command
    from helpers import traceback
    from helpers import misc
    from helpers import modutils
    from helpers import hook
    from configparser import ConfigParser
    from irc.bot import ServerSpec, SingleServerIRCBot
    from irc.connection import Factory
    from os.path import dirname, abspath, join, exists
except ImportError as ex:
    raise Exception("Unable to import all required modules: %s" % ex)


class IrcBot(SingleServerIRCBot):

    def __init__(self, botconfig):
        """Setup everything.

        | Setup the handler.
        | Setup the server.
        | Connect to the server.
        """
        if botconfig.getboolean('core', 'ssl'):
            factory = Factory(wrapper=ssl.wrap_socket, ipv6=botconfig.getboolean('core', 'ipv6'))
        else:
            factory = Factory(ipv6=botconfig.getboolean('core', 'ipv6'))
        passwd = None if botconfig.getboolean('core', 'sasl') else botconfig['auth']['serverpass']
        serverinfo = ServerSpec(botconfig['core']['host'], botconfig.getint('core', 'ircport'), passwd)
        nick = botconfig['core']['nick']
        super().__init__([serverinfo], nick, nick, connect_factory=factory)
        if passwd is None:
            # FIXME: make this less hacky
            self.reactor._on_connect = self.do_sasl
        self.reload_event = threading.Event()
        self.reload_event.set()
        self.config = botconfig

        modutils.init_aux(self.config['core'])
        modutils.init_groups(self.config['groups'])
        commands, errored_commands = command.scan_for_commands('commands')
        if len(errored_commands) > 0:
            print("Failed to reload some commands, things may not work as expected")
            print(", ".join(errored_commands))
            sys.exit(1)
        hooks, errored_hooks = hook.scan_for_hooks('hooks')
        if len(errored_hooks) > 0:
            print("Failed to reload some hooks, there may be significant spam or silent bot failures")
            print(", ".join(errored_hooks))
            sys.exit(1)

        self.handler = handler.BotHandler(botconfig)

        if botconfig['feature'].getboolean('server'):
            self.server = server.init_server(self)
        # properly log quits.
        self.connection.add_global_handler("quit", self.handle_quit, -21)
        # fix unicode problems
        self.connection.buffer_class.errors = 'replace'

    def do_sasl(self, _):
        self.connection.cap('REQ', 'sasl')

    def handle_msg(self, msgtype, c, e):
        """Handles all messages.

        | If a exception is thrown, catch it and display a nice traceback instead of crashing.
        | If we receive a !reload command, do the reloading magic.
GROUPS)       | Call the appropriate handler method for processing.
        """
        if e.target[0] == '#' or e.target[0] == '@' or e.target[0] == '+':
            target = e.target
        else:
            target = e.source.nick
        try:
            self.reload_event.wait()
            reloading = False
            if msgtype != 'mode' and msgtype != 'nick' and msgtype != 'join':
                reloading = self.check_reload(target, c, e, msgtype)
            self.handler.handle_msg(msgtype, c, e)
        except Exception as ex:
            if reloading:
                self.reload_event.set()
            traceback.handle_traceback(ex, c, target, self.config)

    def check_reload(self, target, c, e, msgtype):
        cmd = e.arguments[0].strip()
        if not cmd:
            return False
        cmd = misc.get_cmdchar(self.config, c, cmd, msgtype)
        cmdchar = self.config['core']['cmdchar']
        if cmd.split()[0] == '%sreload' % cmdchar:
            admins = [x.strip() for x in self.config['auth']['admins'].split(',')]
            if e.source.nick not in admins:
                c.privmsg(target, "Nope, not gonna do it.")
                return False
            else:
                cmdargs = cmd[len('%sreload' % cmdchar) + 1:]
                self.do_reload(c, target, cmdargs)
                return True

    def shutdown_server(self):
        if hasattr(self, 'server'):
            self.server.socket.close()
            self.server.shutdown()

    def shutdown_workers(self):
        if hasattr(self, 'handler'):
            self.handler.workers.stop_workers()

    def shutdown_mp(self):
        """ Shutdown all the multiprocessing that we know about, uncleanly """
        self.shutdown_server()
        self.shutdown_workers()

    def kill(self):
        """ forcibly kills everything """
        if hasattr(self, 'handler'):
            self.handler.kill()
        self.shutdown_server()

    def debug_send(self, msg):
        """ Send a message to the control channel, with no dependency on anything but
                our state being valid
        """
        controlchan = self.config['core']['ctrlchan']
        self.connection.privmsg(controlchan, msg)

    def do_reload(self, c, target, cmdargs):
        """The reloading magic.

        | First, reload handler.py.
        | Then make copies of all the handler data we want to keep.
        | Create a new handler and restore all the data.
        """
        self.reload_event.clear()
        output = None
        if cmdargs == 'pull':
            srcdir = dirname(abspath(__file__))
            output = misc.do_pull(srcdir, c.real_nickname)
            c.privmsg(target, output)
        reload_ok = True
        # Reimport helpers
        failed_modules = []
        for name in modutils.get_enabled('helpers', 'helpers')[0]:
            if name in sys.modules:
                mod_reload_ok = modutils.safe_reload(sys.modules[name])
                if not mod_reload_ok:
                    failed_modules.append(name)
                    reload_ok = False
        if not reload_ok:
            self.debug_send("Failed to reload some helper modules. Some commands may not work as expected, see the console for details")
            self.debug_send("Failures: " + ", ".join(failed_modules))
        # reimport the handler
        if not modutils.safe_reload(handler):
            self.debug_send("Failed to reload the helper module, dying")
            self.debug_send("Failures: " + ", ".join(failed_modules))
            sys.exit(1)
        # reimport the commands and hooks
        modutils.init_aux(self.config['core'])
        modutils.init_groups(self.config['groups'])
        commands, errored_commands = command.scan_for_commands('commands')
        if len(errored_commands) > 0:
            self.debug_send("Failed to reload some commands, things may not work as expected")
            self.debug_send(", ".join(errored_commands))
        hooks, errored_hooks = hook.scan_for_hooks('hooks')
        if len(errored_hooks) > 0:
            self.debug_send("Failed to reload some hooks, there may be significant spam or silent bot failures")
            self.debug_send(", ".join(errored_hooks))

        self.config = ConfigParser()
        configfile = join(dirname(__file__), 'config.cfg')
        with open(configfile) as cfgfile:
            self.config.read_file(cfgfile)
        # preserve data
        data = self.handler.get_data()
        self.shutdown_mp()
        self.handler = handler.BotHandler(self.config)
        self.handler.set_data(data)
        self.handler.connection = c
        self.handler.channels = self.channels
        if self.config['feature'].getboolean('server'):
            self.server = server.init_server(self)
        self.reload_event.set()
        if output:
            return output

    @staticmethod
    def get_version():
        """Get the version."""
        return "cslbot - v0.8"

    def do_welcome(self, c):
        """Do setup when connected to server.

        | Pass the connection to handler.
        | Join the primary channel.
        | Join the control channel.
        """
        logging.info("Connected to server %s", self.config['core']['host'])
        self.handler.connection = c
        self.handler.channels = self.channels
        self.handler.get_admins(c)
        c.join(self.config['core']['channel'])
        c.join(self.config['core']['ctrlchan'], self.config['auth']['ctrlkey'])
        extrachans = self.config['core']['extrachans']
        if extrachans:
            extrachans = [x.strip() for x in extrachans.split(',')]
            for i in range(len(extrachans)):
                self.handler.workers.defer(i, False, c.join, extrachans[i])

    def on_pubmsg(self, c, e):
        """Pass public messages to :func:`handle_msg`."""
        self.handle_msg('pubmsg', c, e)

    def on_privmsg(self, c, e):
        """Pass private messages to :func:`handle_msg`."""
        self.handle_msg('privmsg', c, e)

    def on_action(self, c, e):
        """Pass actions to :func:`handle_msg`."""
        self.handle_msg('action', c, e)

    def on_privnotice(self, c, e):
        """Pass private notices to :func:`handle_msg`."""
        self.handle_msg('privnotice', c, e)

    def on_welcome(self, c, _):
        self.do_welcome(c)

    def on_cap(self, c, e):
        if 'ACK sasl' == ' '.join(e.arguments).strip():
            self.connection.send_raw('AUTHENTICATE PLAIN')

    def on_authenticate(self, c, e):
        if e.target == '+':
            passwd = self.config['auth']['serverpass']
            user = self.config['core']['nick']
            token = base64.b64encode('\0'.join([user, user, passwd]).encode())
            self.connection.send_raw('AUTHENTICATE %s' % token.decode())

    def on_903(self, c, e):
        # SASL Successful doesn't have a pretty name.
        if e.arguments[0] == 'SASL authentication successful':
            self.connection.cap('END')

    def on_pubnotice(self, c, e):
        """This is mostly informational stuff from the server that we don't do anything with right now."""
        # self.handle_msg('pubnotice', c, e)

    def on_nick(self, c, e):
        """Log nick changes."""
        for channel in misc.get_channels(self.channels, e.target):
            self.handler.do_log(channel, e.source.nick, e.target, 'nick')
        self.handle_msg('nick', c, e)

    def on_mode(self, c, e):
        """Pass mode changes to :func:`handle_msg`."""
        self.handle_msg('mode', c, e)

    def on_error(self, _, e):
        """Handle ping timeouts."""
        logging.error(e.target)
        # trigger channel joining, etc. on reconnection.
        if hasattr(self.handler, 'connection'):
            delattr(self.handler, 'connection')

    def handle_quit(self, _, e):
        """Log quits."""
        for channel in misc.get_channels(self.channels, e.source.split('!')[0]):
            self.handler.do_log(channel, e.source, e.arguments[0], 'quit')

    def on_disconnect(self, _, e):
        # Don't kill everything if we just ping timed-out
        if e.arguments[0] == 'Goodbye, Cruel World!':
            self.shutdown_mp()

    def on_join(self, c, e):
        """Handle joins."""
        self.handle_msg('join', c, e)

    def on_part(self, c, e):
        """Handle parts.

        | If another user is parting, just log it.
        """
        self.handler.do_log(e.target, e.source, e.target, 'part')
        if e.source.nick != c.real_nickname:
            return
        msg = "Parted channel %s" % e.target
        logging.info(msg)
        c.privmsg(self.config['core']['ctrlchan'], msg)

    def on_bannedfromchan(self, c, e):
        self.handler.workers.defer(5, False, self.do_rejoin, c, e)

    def do_rejoin(self, c, e):
        if e.arguments[0] in self.channels:
            return
        c.join(e.arguments[0])

    @staticmethod
    def on_ctcpreply(c, e):
        if len(e.arguments) == 2:
            misc.ping(c, e, time.time())

    def on_nicknameinuse(self, c, _):
        self.connection.nick('Guest%d' % random.getrandbits(20))
        self.connection.send_raw('NS REGAIN %s %s' % (self.config['core']['nick'], self.config['auth']['serverpass']))
        self.handler.workers.defer(5, False, self.do_welcome, c)

    def on_kick(self, c, e):
        """Handle kicks.

        | If somebody else was kicked, just log it.
        | Record who kicked us and what for to use in :func:`on_join`.
        | Wait 5 seconds and then rejoin.
        """
        self.handler.do_log(e.target, e.source.nick, ','.join(e.arguments), 'kick')
        # we don't care about other people.
        if e.arguments[0] != c.real_nickname:
            return
        logging.info("Kicked from channel %s", e.target)
        self.handler.workers.defer(5, False, c.join, e.target)


def main(args):
    """The bot's main entry point.

    | Setup logging.
    | When troubleshooting startup, it may help to change the INFO to DEBUG.
    | Initialize the bot and start processing messages.
    """
    loglevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=loglevel)
    botconfig = ConfigParser()
    configfile = join(dirname(__file__), 'config.cfg')
    if not exists(configfile):
        print("Setting up config file")
        config.do_setup(configfile)
        return
    with open(configfile) as conf:
        botconfig.read_file(conf)
    bot = IrcBot(botconfig)
    try:
        bot.start()
    except KeyboardInterrupt:
        # keyboard interrupt means someone tried to ^C, shut down the bot
        bot.kill()
        sys.exit(0)
    except Exception as e:
        bot.kill()
        logging.error("The bot died! %s" % (e))
        (typ3, value, tb) = sys.exc_info()
        errmsg = "".join(traceback.format_exception(typ3, value, tb))
        for line in errmsg.split('\n'):
            logging.error(errmsg)
        sys.exit(1)

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debug logging.', action='store_true')
    parser_args = parser.parse_args()
    main(parser_args)
