#!/usr/bin/python3 -O
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import logging
import imp
import sys
import handler
import argparse
import atexit
from helpers import workers, server, config, defer, traceback, misc, modutils
from configparser import ConfigParser
from irc.bot import ServerSpec, SingleServerIRCBot
from os.path import dirname, join, exists
from time import time
from random import getrandbits


class IrcBot(SingleServerIRCBot):

    def __init__(self, botconfig):
        """Setup everything.

        | Setup the handler.
        | Setup the server.
        | Connect to the server.
        """
        atexit.register(self.do_shutdown)
        self.handler = handler.BotHandler(botconfig)
        self.config = botconfig
        serverinfo = ServerSpec(botconfig['core']['host'], int(botconfig['core']['ircport']), botconfig['auth']['nickpass'])
        nick = botconfig['core']['nick']
        SingleServerIRCBot.__init__(self, [serverinfo], nick, nick)
        # properly log quits.
        self.connection.add_global_handler("quit", self.handle_quit, -21)
        # fix unicode problems
        self.connection.buffer_class.errors = 'replace'

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
            if msgtype != 'mode' and msgtype != 'nick' and msgtype != 'join':
                self.check_reload(target, c, e, msgtype)
            self.handler.handle_msg(msgtype, c, e)
        except Exception as ex:
            traceback.handle_traceback(ex, c, target)

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
                self.do_reload(c, target, cmdargs, 'irc')

    def do_shutdown(self):
        self.server.shutdown()
        self.server.socket.close()
        # blocks on the message processing otherwise.
        self.handler.executor.shutdown(False)
        # threading cleanup
        workers.stop_workers()

    def do_reload(self, c, target, cmdargs, msgtype):
        """The reloading magic.

        | First, reload handler.py.
        | Then make copies of all the handler data we want to keep.
        | Create a new handler and restore all the data.
        """
        output = None
        if cmdargs == 'pull':
            output = misc.do_pull(dirname(__file__), c.real_nickname)
            c.privmsg(target, output)
        for x in modutils.get_enabled(dirname(__file__) + '/helpers'):
            imp.reload(sys.modules['helpers.%s' % x])
        imp.reload(handler)
        self.config = ConfigParser()
        configfile = join(dirname(__file__), 'config.cfg')
        self.config.read_file(open(configfile))
        # preserve data
        data = self.handler.get_data()
        self.do_shutdown()
        self.handler = handler.BotHandler(self.config)
        self.server = server.init_server(self)
        self.handler.set_data(data)
        self.handler.connection = c
        self.handler.channels = self.channels
        workers.start_workers(self.handler)
        if output:
            return output

    def get_version(self):
        """Get the version."""
        return "cslbot - v0.5"

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
        workers.start_workers(self.handler)
        extrachans = self.config['core']['extrachans']
        if extrachans:
            extrachans = [x.strip() for x in extrachans.split(',')]
            for i in range(len(extrachans)):
                defer.defer(i, c.join, extrachans[i])

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
        delattr(self.handler, 'connection')

    def handle_quit(self, c, e):
        """Log quits."""
        for channel in misc.get_channels(self.channels, e.source.split('!')[0]):
            self.handler.do_log(channel, e.source, e.arguments[0], 'quit')

    def on_disconnect(self, c, e):
        self.do_shutdown()

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
        # FIXME: Implement auto-rejoin on ban.
        defer.defer(5, c.join, e.arguments[0])

    def on_ctcpreply(self, c, e):
        misc.ping(c, e, time())

    def on_nicknameinuse(self, c, e):
        self.connection.nick('Guest%d' % getrandbits(20))
        self.connection.privmsg('NickServ', 'REGAIN %s %s' % (self.config['core']['nick'], self.config['auth']['nickpass']))
        defer.defer(5, self.do_welcome, c)

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
        defer.defer(5, c.join, e.target)


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
    botconfig.read_file(open(configfile))
    bot = IrcBot(botconfig)
    bot.server = server.init_server(bot)
    bot.start()

if __name__ == '__main__':
    if sys.version_info < (3, 3):
        raise Exception("Need Python 3.3 or higher.")
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Enable debug logging.', action='store_true')
    args = parser.parse_args()
    main(args)
