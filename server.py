import threading
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

import socketserver
from config import SERVERPORT, CTRLPASS

WELCOME = """
Welcome to the IRCbot console.
Copyright (c) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, and James Forcier.
Licensed under the GNU GPL version 2.

Type "help" for a list of commands.
"""
HELP = """
== IRCbot console commands list ==
help: show this help
admins: show the list of admins
quit: quit the console session
"""


def init_server(bot):
    server = BotNetServer(('', SERVERPORT), BotNetHandler)
    server.bot = bot
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server


class BotNetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class BotNetHandler(socketserver.BaseRequestHandler):
    def get_data(self):
        SIZE = 4096
        msg = ""
        while True:
            data = self.request.recv(SIZE).decode()
            msg += data
            if len(data) != SIZE:
                break
        return msg

    def handle(self):
        send = lambda msg: self.request.send(msg.encode())
        send("Password: ")
        msg = self.get_data().splitlines()
        if msg[0].strip() == CTRLPASS:
            send(WELCOME)
        else:
            send("Incorrect password.\n")
            self.request.close()
            return
        if len(msg) > 1:
            msg = list(reversed(msg[1:]))
            end = len(msg)
        while True:
            if end:
                cmd = msg[end-1].strip()
                end -= 1
            else:
                try:
                    send("ircbot> ")
                    cmd = self.get_data().strip()
                except OSError:
                    # connection has been closed
                    return
            if cmd == "help":
                send(HELP)
            elif cmd == "admins":
                admins = ", ".join(self.server.bot.handler.admins.keys())
                send(admins + '\n')
            elif cmd == "raw":
                while cmd != "endraw":
                    send("ircbot-raw> ")
                    cmd = self.get_data().strip()
                    if cmd == "endraw":
                        break
                    self.server.bot.handler.connection.send_raw(cmd)
                continue
            elif cmd == "quit":
                send("Goodbye.\n")
                self.request.close()
                break
            else:
                send("Unknown command. Type help for more info.\n")
