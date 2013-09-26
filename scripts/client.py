#!/usr/bin/python3 -OO
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
import sys
from configparser import ConfigParser
from irc.client import SimpleIRCClient


class IrcClient(SimpleIRCClient):

    def __init__(self, nick, config):
        self.nick = nick
        self.config = config
        self.loading = False
        SimpleIRCClient.__init__(self)

    def on_welcome(self, c, e):
        c.join(self.config['core']['ctrlchan'], self.config['auth']['ctrlkey'])

    def on_mode(self, c, e):
        if self.loading:
            return
        if e.arguments[0] == "+o" and e.arguments[1] == self.nick:
            cmdchar = self.config['core']['cmdchar']
            c.privmsg(self.config['core']['ctrlchan'], '%sreload' % cmdchar)
            self.loading = True

    def on_join(self, c, e):
        c.mode(self.config['core']['ctrlchan'], "")

    def on_channelmodeis(self, c, e):
        if self.loading:
            return
        if "m" not in e.arguments[1]:
            cmdchar = self.config['core']['cmdchar']
            c.privmsg(self.config['core']['ctrlchan'], '%sreload' % cmdchar)
            self.loading = True

    def on_pubmsg(self, c, e):
        ctrlchan = self.config['core']['ctrlchan']
        if e.source.nick == self.config['core']['nick']:
            if e.arguments[0] == "Aye Aye Capt'n":
                print("Reload successful.")
                c.part(ctrlchan)
                c.quit()
                sys.exit(0)
            else:
                print("Reload failed.")
                c.part(ctrlchan)
                c.quit()
                sys.exit(1)


def main():
    logging.basicConfig(level=logging.INFO)
    config = ConfigParser()
    config.read_file(open('config.cfg'))
    PORT = 6667
    CTRLNICK = "bot-controller"
    client = IrcClient(CTRLNICK, config)
    client.connect(config['core']['host'], PORT, CTRLNICK, config['auth']['ctrlpass'])
    client.start()

if __name__ == '__main__':
    main()
