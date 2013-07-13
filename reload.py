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
import sys
from irc.client import SimpleIRCClient
from config import CTRLCHAN, CTRLPASS, NICK, HOST, CTRLKEY


class IrcClient(SimpleIRCClient):
    def __init__(self, nick):
        self.nick = nick
        self.loading = False
        SimpleIRCClient.__init__(self)

    def on_welcome(self, c, e):
        c.join(CTRLCHAN, CTRLKEY)

    def on_mode(self, c, e):
        if self.loading:
            return
        if e.arguments[0] == "+o" and e.arguments[1] == self.nick:
            c.privmsg(CTRLCHAN, '!reload')
            self.loading = True

    def on_join(self, c, e):
        c.mode(CTRLCHAN, "")

    def on_channelmodeis(self, c, e):
        if self.loading:
            return
        if "m" not in e.arguments[1]:
            c.privmsg(CTRLCHAN, '!reload')
            self.loading = True

    def on_pubmsg(self, c, e):
        if e.source.nick == NICK:
            if e.arguments[0] == "Aye Aye Capt'n":
                print("Reload successful.")
                c.quit()
                sys.exit(0)
            else:
                print("Reload failed.")
                c.quit()
                sys.exit(1)


def main():
    logging.basicConfig(level=logging.INFO)
    PORT = 6667
    CTRLNICK = "bot-controller"
    client = IrcClient(CTRLNICK)
    client.connect(HOST, PORT, CTRLNICK, CTRLPASS)
    client.start()

if __name__ == '__main__':
    main()
