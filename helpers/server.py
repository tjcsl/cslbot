# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from .traceback import get_traceback
from .thread import start

WELCOME = """
Welcome to the IRCbot console.
Copyright (c) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, and James Forcier.
Licensed under the GNU GPL version 2.

Type "help" for a list of commands.
"""
HELP = """
help\t\t\tshow this help
admins\t\t\tshow the list of admins
reload\t\t\treload the bot
raw\t\t\tenter raw mode
endraw\t\t\texit raw mode
quit\t\t\tquit the console session
"""


def init_server(bot):
    port = bot.config.getint('core', 'serverport')
    server = BotNetServer(('', port), BotNetHandler)
    server.bot = bot
    start(server.serve_forever)
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
        try:
            def send(msg):
                self.request.send(msg.encode())
            bot = self.server.bot
            send("Password: ")
            msg = self.get_data().splitlines()
            ctrlpass = bot.config['auth']['ctrlpass']
            if not msg or msg[0].strip() != ctrlpass:
                send("Incorrect password.\n")
                self.request.close()
                return
            if len(msg) > 1:
                msg = list(reversed(msg[1:]))
                end = len(msg)
                send("\n")
            else:
                send(WELCOME)
                end = 0
            while True:
                if end:
                    cmd = msg[end - 1].strip().split()
                    end -= 1
                else:
                    try:
                        send("ircbot> ")
                        cmd = self.get_data().strip().split()
                    except Exception:
                        # connection has been closed
                        return
                if not cmd:
                    continue
                if cmd[0] == "help":
                    send(HELP)
                elif cmd[0] == "admins":
                    admins = ", ".join(bot.handler.admins.keys())
                    send(admins + '\n')
                elif cmd[0] == "reload":
                    cmdargs = cmd[1] if len(cmd) > 1 else ''
                    ctrlchan = bot.config['core']['ctrlchan']
                    output = bot.do_reload(bot.connection, ctrlchan, cmdargs, 'server')
                    bot.handler.do_reload()
                    if output:
                        send(output + '\n')
                    send("Aye Aye Capt'n\n")
                    bot.connection.privmsg(ctrlchan, "Aye Aye Capt'n (triggered from server)")
                    self.request.close()
                    break
                elif cmd[0] == "raw":
                    while cmd[0] != "endraw":
                        send("ircbot-raw> ")
                        cmd = self.get_data().strip()
                        if cmd == "endraw":
                            break
                        bot.handler.connection.send_raw(cmd)
                    continue
                elif cmd[0] == "quit":
                    send("Goodbye.\n")
                    self.request.close()
                    break
                else:
                    send("Unknown command. Type help for more info.\n")
        except Exception as ex:
            msg, _ = get_traceback(ex)
            ctrlchan = bot.config['core']['ctrlchan']
            send(msg + '\n')
            bot.connection.privmsg(ctrlchan, msg)
