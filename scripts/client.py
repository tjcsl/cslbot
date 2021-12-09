#!/usr/bin/env python3
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

import configparser
import logging
import ssl
import sys

from irc import client, connection


class IrcClient(client.SimpleIRCClient):

    def __init__(self, nick: str, config: configparser.ConfigParser) -> None:
        self.nick = nick
        self.config = config
        self.loading = False
        super().__init__()

    def on_welcome(self, c, _):
        c.join(self.config['core']['ctrlchan'], self.config['auth']['ctrlkey'])

    def on_mode(self, c, e):
        if self.loading:
            return
        if e.arguments[0] == "+o" and e.arguments[1] == self.nick:
            cmdchar = self.config['core']['cmdchar']
            c.privmsg(self.config['core']['ctrlchan'], '%sreload' % cmdchar)
            self.loading = True

    def on_join(self, c, _):
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


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    with open('config.cfg') as f:
        config.read_file(f)
    ctrl_nick = "bot-controller"
    ircclient = IrcClient(ctrl_nick, config)
    if config.getboolean('core', 'ssl'):
        factory = connection.Factory(wrapper=ssl.wrap_socket, ipv6=config.getboolean('core', 'ipv6'))
    else:
        factory = connection.Factory(ipv6=config.getboolean('core', 'ipv6'))
    for host in config['core']['host'].split(','):
        ircclient.connect(host.strip(), config.getint('core', 'ircport'), ctrl_nick, config['auth']['serverpass'], connect_factory=factory)
        ircclient.start()


if __name__ == '__main__':
    main()
