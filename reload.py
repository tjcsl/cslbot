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
from config import CTRLCHAN, NICK, NICKPASS, HOST, CTRLKEY


class IrcClient(SimpleIRCClient):
    def on_welcome(self, c, e):
        c.join(CTRLCHAN, CTRLKEY)

    def on_join(self, c, e):
        c.privmsg(CTRLCHAN, '!reload')

    def on_pubmsg(self, c, e):
        if e.source.nick == NICK:
            if e.arguments[0] == "Aye Aye Capt'n":
                print("Reload successful.")
                sys.exit(0)
            else:
                print("Reload failed.")
                sys.exit(1)


def main():
    logging.basicConfig(level=logging.INFO)
    client = IrcClient()
    PORT = 6667
    NICK = "bot-controller"
    client.connect(HOST, PORT, NICK, NICKPASS)
    client.start()

if __name__ == '__main__':
    main()
