#!/usr/bin/python3 -OO
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
import irc.bot
from config import CHANNEL, NICK, NICKPASS, HOST
from os.path import basename
import handler


class MyBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nick, nickpass, host, port=6667):
        if nickpass != '':
            server = irc.bot.ServerSpec(host, port, nickpass)
        else:
            server = irc.bot.ServerSpec(host, port)
        irc.bot.SingleServerIRCBot.__init__(self, [server], nick, nick)
        self.handler = handler.MyHandler()

    def on_welcome(self, c, e):
        """Do setup when connected to server.

        | Pass the connection to handler.
        | Join the primary channel.
        """
        logging.info("Connected to server " + HOST)
        self.handler.connection = c
        c.join(CHANNEL)

    def on_join(self, c, e):
        """Add the joined channel to the channel list."""
        self.handler.channels[e.target] = self.channels[e.target]
        logging.info("Joined channel " + e.target)

    def on_part(self, c, e):
        """Cleanup when leaving a channel."""
        #FIXME: this breaks randomly
        # del self.handler.channels[e.target]
        logging.info("Parted channel " + e.target)

    def do_reload(self, c):
        """The reloading magic

        | First, reload handler.py.
        | Then make copies of all the handler data we want to keep.
        | Create a new handler and restore all the data.
        """
        imp.reload(handler)
        # preserve logs, ignored list, and channel list
        ignored = list(self.handler.ignored)
        logs = dict(self.handler.logs)
        logfiles = dict(self.handler.logfiles)
        channels = dict(self.handler.channels)
        self.handler = handler.MyHandler()
        self.handler.ignored = ignored
        self.handler.logs = logs
        self.handler.logfiles = logfiles
        self.handler.channels = channels
        self.handler.connection = c

    def handle_msg(self, msgtype, c, e):
        """Handles all messages.

        | If a exception is thrown, catch it and display a nice traceback instead of crashing.
        | If we receive a !reload command, do the reloading magic.
        | Call the appropriate handler method for processing.
        """
        try:
            command = e.arguments[0].strip()
            if not command:
                return
            if command.split()[0] == '!reload':
                self.do_reload(c)
            getattr(self.handler, msgtype)(c, e)
        except Exception as ex:
            trace = traceback.extract_tb(ex.__traceback__)[-1]
            trace = [basename(trace[0]), trace[1]]
            name = type(ex).__name__
            target = CHANNEL if msgtype == 'pubmsg' else e.source.nick
            c.privmsg(target, '%s in %s on line %s: %s' % (name, trace[0], trace[1], str(ex)))

    def on_pubmsg(self, c, e):
        """Pass public messages to the handler."""
        self.handle_msg('pubmsg', c, e)

    def on_privmsg(self, c, e):
        """Pass private messages to the handler."""
        self.handle_msg('privmsg', c, e)

    def on_action(self, c, e):
        """Pass actions to the handler."""
        self.handle_msg('action', c, e)

    def get_version(self):
        """Get the version."""
        return "Ircbot -- 1.0"


def main():
    """The bot's main entry point.

    | Setup logging.
    | When troubleshooting, it may help to change the INFO to DEBUG.
    | Initialize the bot and start processing messages.
    """
    logging.basicConfig(level=logging.INFO)
    bot = MyBot(CHANNEL, NICK, NICKPASS, HOST)
    bot.start()

if __name__ == '__main__':
    main()
