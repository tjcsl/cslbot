#!/usr/bin/python3 -O
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
import traceback
import imp
import sys
import handler
from helpers.server import init_server
from helpers.config import do_setup
from commands.pull import do_pull
from configparser import ConfigParser
from irc.bot import ServerSpec, SingleServerIRCBot
from os.path import basename, dirname, join, exists
from time import sleep


class IrcBot(SingleServerIRCBot):

    def __init__(self, config):
        """Setup everything.

        | Setup the handler.
        | Setup the server.
        | Connect to the server.
        """
        self.handler = handler.BotHandler(config)
        self.config = config
        serverinfo = ServerSpec(config['core']['host'], int(config['core']['ircport']), config['auth']['nickpass'])
        nick = config['core']['nick']
        SingleServerIRCBot.__init__(self, [serverinfo], nick, nick)
        # fix unicode problems
        self.connection.buffer_class.errors = 'replace'

    def handle_msg(self, msgtype, c, e):
        """Handles all messages.

        | If a exception is thrown, catch it and display a nice traceback instead of crashing.
        | If we receive a !reload command, do the reloading magic.
        | Call the appropriate handler method for processing.
        """
        target = e.target if e.target[0] == '#' else e.source.nick
        try:
            cmd = e.arguments[0].strip()
            if not cmd:
                return
            cmdchar = self.config['core']['cmdchar']
            if cmd.split()[0] == '%sreload' % cmdchar:
                admins = [x.strip() for x in self.config['auth']['admins'].split(',')]
                if e.source.nick not in admins:
                    c.privmsg(target, "Nope, not gonna do it.")
                else:
                    cmdargs = cmd[len('%sreload' % cmdchar) + 1:]
                    self.do_reload(c, target, cmdargs, 'irc')
            self.handler.handle_msg(msgtype, c, e)
        except Exception as ex:
            trace = traceback.extract_tb(ex.__traceback__)[-1]
            trace = [basename(trace[0]), trace[1]]
            name = type(ex).__name__
            c.privmsg(target, '%s in %s on line %s: %s' % (name, trace[0], trace[1], str(ex)))

    def do_reload(self, c, target, cmdargs, msgtype):
        """The reloading magic.

        | First, reload handler.py.
        | Then make copies of all the handler data we want to keep.
        | Create a new handler and restore all the data.
        """
        output = None
        if cmdargs == 'pull':
            output = do_pull(dirname(__file__), c.real_nickname)
            c.privmsg(target, output)
        imp.reload(sys.modules['helpers'])
        imp.reload(handler)
        self.config = ConfigParser()
        configfile = join(dirname(__file__), 'config.cfg')
        self.config.read_file(open(configfile))
        self.server.shutdown()
        self.server.socket.close()
        self.server = init_server(self)
        # preserve data
        data = self.handler.get_data()
        self.handler = handler.BotHandler(self.config)
        self.handler.set_data(data)
        self.handler.connection = c
        if output:
            return output

    def get_version(self):
        """Get the version."""
        return "cslbot - v0.4"

    def on_welcome(self, c, e):
        """Do setup when connected to server.

        | Pass the connection to handler.
        | Join the primary channel.
        | Join the control channel.
        """
        logging.info("Connected to server %s" % self.config['core']['host'])
        self.handler.connection = c
        self.handler.get_admins(c)
        c.join(self.config['core']['channel'])
        c.join(self.config['core']['ctrlchan'], self.config['auth']['ctrlkey'])
        for i in self.config['core']['extrachans']:
            c.join(i)

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

    def on_pubnotice(self, c, e):
        """Pass public notices to :func:`handle_msg`."""
        self.handle_msg('pubnotice', c, e)

    def on_nick(self, c, e):
        """Log nick changes."""
        # Nick changes don't have a associated channel, so we just use the default channel.
        self.handler.do_log(self.config['core']['channel'], e.source.nick, e.target, 'nick')

    def on_mode(self, c, e):
        """Pass mode changes to :func:`handle_msg`."""
        self.handle_msg('mode', c, e)

    #FIXME: do something.
    #def on_disconnect(self, c, e):
        """Handle ping timeouts."""

    def on_quit(self, c, e):
        """Log quits."""
        # Quits don't have a associated channel, so we just use the default channel.
        self.handler.do_log(self.config['core']['channel'], e.source, e.arguments[0], 'quit')

    def on_join(self, c, e):
        """Handle joins.

        | If another user has joined, just log it.
        | Add the joined channel to the channel list.
        | If we've been kicked, yell at the kicker.
        """
        self.handler.do_log(e.target, e.source, e.target, 'join')
        if e.source.nick != c.real_nickname:
            return
        self.handler.channels[e.target] = self.channels[e.target]
        logging.info("Joined channel %s" % e.target)
        if hasattr(self, 'kick'):
            #slogan = self.handler.modules['slogan'].gen_slogan("power abuse")
            #c.privmsg(e.target, slogan)
            del self.kick

    def on_part(self, c, e):
        """Handle parts.

        | If another user is parting, just log it.
        | Remove the channel from the list of channels.
        """
        self.handler.do_log(e.target, e.source, e.target, 'part')
        if e.source.nick != c.real_nickname:
            return
        del self.handler.channels[e.target]
        logging.info("Parted channel %s" % e.target)

    def on_bannedfromchan(self, c, e):
        # FIXME: Implement auto-rejoin on ban.
        sleep(5)
        c.join(e.arguments[0])

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
        self.kick = [e.source.nick, e.arguments[1]]
        sleep(5)
        c.join(e.target)


def main():
    """The bot's main entry point.

    | Setup logging.
    | When troubleshooting startup, it may help to change the INFO to DEBUG.
    | Initialize the bot and start processing messages.
    """
    logging.basicConfig(level=logging.INFO)
    config = ConfigParser()
    configfile = join(dirname(__file__), 'config.cfg')
    if not exists(configfile):
        print("Setting up config file")
        do_setup(configfile)
        return
    config.read_file(open(configfile))
    bot = IrcBot(config)
    bot.server = init_server(bot)
    bot.start()

if __name__ == '__main__':
    if sys.version_info < (3, 3):
        raise Exception("Need Python 3.3 or higher.")
    main()
