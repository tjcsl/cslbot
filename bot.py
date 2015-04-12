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
    import importlib
    import argparse
    import ssl
    import handler
    import threading
    import multiprocessing
    import helpers.server as server
    import helpers.config as config
    import helpers.traceback as traceback
    import helpers.misc as misc
    import helpers.modutils as modutils
    from configparser import ConfigParser
    from irc.bot import ServerSpec, SingleServerIRCBot
    from irc.connection import Factory
    from os.path import dirname, join, exists
    from time import time
    from random import getrandbits
except ImportError as e:
    raise Exception("Unable to import all required modules: %s" % e)


class IrcBot(SingleServerIRCBot):

    def __init__(self, botconfig):
        """Setup everything.

        | Setup the handler.
        | Setup the server.
        | Connect to the server.
        """
        self.reload_event = threading.Event()
        self.reload_event.set()
        self.config = botconfig
        self.handler = handler.BotHandler(botconfig)
        if botconfig['feature'].getboolean('server'):
            self.server = server.init_server(self)
        serverinfo = ServerSpec(botconfig['core']['host'], int(botconfig['core']['ircport']), botconfig['auth']['serverpass'])
        nick = botconfig['core']['nick']
        self.handle_connect(serverinfo, nick, botconfig['core'])
        # properly log quits.
        self.connection.add_global_handler("quit", self.handle_quit, -21)
        # fix unicode problems
        self.connection.buffer_class.errors = 'replace'

    def handle_connect(self, serverinfo, nick, botconfig):
        ipv6 = botconfig.getboolean('ipv6')
        if botconfig.getboolean('ssl'):
            SingleServerIRCBot.__init__(self, [serverinfo], nick, nick, connect_factory=Factory(wrapper=ssl.wrap_socket, ipv6=ipv6))
        else:
            SingleServerIRCBot.__init__(self, [serverinfo], nick, nick, connect_factory=Factory(ipv6=ipv6))

    def handle_msg(self, msgtype, c, e):
        """Handles all messages.

        | If a exception is thrown, catch it and display a nice traceback instead of crashing.
        | If we receive a !reload command, do the reloading magic.
        | Call the appropriate handler method for processing.
        """
        if e.target[0] == '#' or e.target[0] == '@' or e.target[0] == '+':
            target = e.target
        else:
            target = e.source.nick
        try:
            self.reload_event.wait()
            if msgtype != 'mode' and msgtype != 'nick' and msgtype != 'join':
                self.check_reload(target, c, e, msgtype)
            self.handler.handle_msg(msgtype, c, e)
        except Exception as ex:
            traceback.handle_traceback(ex, c, target, self.config)

    def check_reload(self, target, c, e, msgtype):
        cmd = e.arguments[0].strip()
        if not cmd:
            return
        cmd = misc.get_cmdchar(self.config, c, cmd, msgtype)
        cmdchar = self.config['core']['cmdchar']
        if cmd.split()[0] == '%sreload' % cmdchar:
            admins = [x.strip() for x in self.config['auth']['admins'].split(',')]
            if e.source.nick not in admins:
                c.privmsg(target, "Nope, not gonna do it.")
            else:
                cmdargs = cmd[len('%sreload' % cmdchar) + 1:]
                self.do_reload(c, target, cmdargs)

    def shutdown_server(self):
        if hasattr(self, 'server'):
            self.server.socket.close()
            self.server.shutdown()

    def shutdown_workers(self):
        if hasattr(self, 'handler'):
            self.handler.workers.stop_workers()

    def do_reload(self, c, target, cmdargs):
        """The reloading magic.

        | First, reload handler.py.
        | Then make copies of all the handler data we want to keep.
        | Create a new handler and restore all the data.
        """
        self.reload_event.clear()
        output = None
        if cmdargs == 'pull':
            output = misc.do_pull(dirname(__file__), c.real_nickname)
            c.privmsg(target, output)
        for name in modutils.get_enabled('helpers', 'helpers')[0]:
            if name in sys.modules:
                importlib.reload(sys.modules[name])
        importlib.reload(handler)
        self.config = ConfigParser()
        configfile = join(dirname(__file__), 'config.cfg')
        with open(configfile) as cfgfile:
            self.config.read_file(cfgfile)
        # preserve data
        data = self.handler.get_data()
        self.shutdown_server()
        self.shutdown_workers()
        self.handler = handler.BotHandler(self.config)
        self.handler.set_data(data)
        self.handler.connection = c
        self.handler.channels = self.channels
        if self.config['feature'].getboolean('server'):
            self.server = server.init_server(self)
        self.reload_event.set()
        if output:
            return output

    def get_version(self):
        """Get the version."""
        return "cslbot - v0.8"

    def do_welcome(self, c):
        """Do setup when connected to server.

        | Pass the connection to handler.
        | Join the primary channel.
        | Join the control channel.
        """
        logging.info("Connected to server %s" % self.config['core']['host'])
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

    def on_welcome(self, c, e):
        self.do_welcome(c)

    def on_pubnotice(self, c, e):
        """Pass public notices to :func:`handle_msg`."""
        self.handle_msg('pubnotice', c, e)

    def on_nick(self, c, e):
        """Log nick changes."""
        for channel in misc.get_channels(self.channels, e.target):
            self.handler.do_log(channel, e.source.nick, e.target, 'nick')
        self.handle_msg('nick', c, e)

    def on_mode(self, c, e):
        """Pass mode changes to :func:`handle_msg`."""
        self.handle_msg('mode', c, e)

    def on_error(self, c, e):
        """Handle ping timeouts."""
        logging.error(e.target)
        # trigger channel joining, etc. on reconnection.
        if hasattr(self.handler, 'connection'):
            delattr(self.handler, 'connection')

    def handle_quit(self, c, e):
        """Log quits."""
        for channel in misc.get_channels(self.channels, e.source.split('!')[0]):
            self.handler.do_log(channel, e.source, e.arguments[0], 'quit')

    def on_disconnect(self, c, e):
        # Don't kill everything if we just ping timed-out
        if e.arguments[0] == 'Goodbye, Cruel World!':
            self.shutdown_server()
            self.shutdown_workers()

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

    def on_ctcpreply(self, c, e):
        if len(e.arguments) == 2:
            misc.ping(c, e, time())

    def on_nicknameinuse(self, c, e):
        self.connection.nick('Guest%d' % getrandbits(20))
        self.connection.send_raw('NS REGAIN %s %s' % (self.config['core']['nick'], self.config['auth']['nickpass']))
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
        logging.info("Kicked from channel %s" % e.target)
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
    bot.start()

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debug logging.', action='store_true')
    args = parser.parse_args()
    main(args)
