#!/usr/bin/python3 -O
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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
import handler
import server
import control
from configparser import ConfigParser
from irc.bot import ServerSpec, SingleServerIRCBot
from os.path import basename, dirname
from time import sleep


class IrcBot(SingleServerIRCBot):

    def __init__(self, config, port=6667):
        """Setup everything.

        | Setup the handler.
        | Setup the server.
        | Connect to the server.
        """
        self.handler = handler.BotHandler(config)
        self.config = config
        serverinfo = ServerSpec(config.get('core', 'host'), port, config.get('auth', 'nickpass'))
        nick = config.get('core', 'nick')
        SingleServerIRCBot.__init__(self, [serverinfo], nick, nick)
        #fix unicode problems
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
            if cmd.split()[0] == '!reload':
                admins = self.config.get('auth', 'admins').split(', ')
                if e.source.nick not in admins:
                    c.privmsg(target, "Nope, not gonna do it.")
                    return
                cmdargs = cmd[len('!reload') + 1:]
                self.do_reload(c, target, cmdargs, 'irc')
            getattr(self.handler, msgtype)(c, e)
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
            output = self.handler.modules['pull'].do_pull(dirname(__file__), self.config.get('core', 'nick'))
            c.privmsg(target, output)
        imp.reload(handler)
        imp.reload(server)
        imp.reload(control)
        self.config = ConfigParser()
        self.config.read_file(open(dirname(__file__)+'/config.cfg'))
        self.server.shutdown()
        self.server.socket.close()
        self.server = server.init_server(self)
        # preserve data
        data = self.handler.get_data()
        self.handler = handler.BotHandler(self.config)
        self.handler.set_data(data)
        self.handler.get_admins(c)
        self.handler.connection = c
        if output:
            return output

    def get_version(self):
        """Get the version."""
        return "IrcBot -- 1.0"

    def on_welcome(self, c, e):
        """Do setup when connected to server.

        | Pass the connection to handler.
        | Join the primary channel.
        | Join the control channel.
        """
        logging.info("Connected to server %s" % self.config.get('core', 'host'))
        self.handler.connection = c
        self.handler.get_admins(c)
        c.join(self.config.get('core', 'channel'))
        c.join(self.config.get('core', 'ctrlchan'), self.config.get('auth', 'ctrlkey'))

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
        """Pass privnotices to :func:`handle_msg`."""
        self.handle_msg('privnotice', c, e)

    def on_nick(self, c, e):
        """Log nick changes."""
        self.handler.do_log(self.config.get('core', 'channel'), e.source.nick, e.target, 'nick')

    def on_mode(self, c, e):
        """Pass mode changes to :func:`handle_msg`."""
        self.handle_msg('mode', c, e)

    def on_quit(self, c, e):
        """Log quits."""
        self.handler.do_log(self.config.get('core', 'channel'), e.source, e.arguments[0], 'quit')

    def on_join(self, c, e):
        """Handle joins.

        | If another user has joined, just log it.
        | Add the joined channel to the channel list.
        | If we've been kicked, yell at the kicker.
        """
        self.handler.do_log(e.target, e.source, e.target, 'join')
        if e.source.nick != self.config.get('core', 'nick'):
            return
        self.handler.channels[e.target] = self.channels[e.target]
        logging.info("Joined channel " + e.target)
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
        if e.source.nick != self.config.get('core', 'nick'):
            return
        del self.handler.channels[e.target]
        logging.info("Parted channel " + e.target)

    def on_bannedfromchan(self, c, e):
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
        if e.arguments[0] != self.config.get('core', 'nick'):
            return
        logging.info("Kicked from channel " + e.target)
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
    config.read_file(open(dirname(__file__)+'/config.cfg'))
    bot = IrcBot(config)
    bot.server = server.init_server(bot)
    bot.start()

if __name__ == '__main__':
    main()
