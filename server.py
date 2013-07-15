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


class BotNetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class BotNetHandler(socketserver.BaseRequestHandler):
    def handle(self):
        send = lambda msg: self.request.send(msg.encode())
        recv = lambda: self.request.recv(1024).decode().strip()
        send("Password: ")
        if recv() == CTRLPASS:
            send(WELCOME)
        else:
            send("Incorrect password.\n")
            self.request.close()
            return
        while True:
            try:
                send("ircbot> ")
            except OSError:
                # connection has been closed
                return
            try:
                cmd = recv()
            except:
                # connection has been closed (ctrl+c or similar)
                return
            if cmd == "help":
                send(HELP)
            elif cmd == "admins":
                admins = ", ".join(self.server.bot.handler.admins.keys())
                send(admins+'\n')
            elif cmd == "raw":
                while cmd != "endraw":
                    send("ircbot-raw> ")
                    cmd = recv()
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
