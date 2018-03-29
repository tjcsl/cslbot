# -*- coding: utf-8 -*-
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

import socketserver

from irc import client

from . import backtrace, reloader

WELCOME = """
Welcome to the IRCbot console.
Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
Licensed under the GNU GPL version 2.

Type "help" for a list of commands.
"""

HELP = """
help\t\t\tshow this help
reload\t\t\treload the bot
raw\t\t\tenter raw mode
endraw\t\t\texit raw mode
quit\t\t\tquit the console session
"""


def init_server(bot):
    port = bot.config.getint('core', 'serverport')
    try:
        server = BotNetServer(('localhost', port), BotNetHandler)
    except OSError as ex:
        bot.shutdown_mp()
        if ex.errno == 98:
            raise Exception("Please make sure that there is no other service running on port %d" % port)
        else:
            raise ex
    server.bot = bot
    bot.handler.workers.start_thread(server.serve_forever)
    return server


class BotNetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class BotNetHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        size = 4096
        msg = "".encode()
        while True:
            data = self.request.recv(size)
            msg += data
            if len(data) != size:
                break
        return msg.decode()

    def handle_cmd(self, cmd, bot, send):
        if cmd[0] == "help":
            send(HELP)
        elif cmd[0] == "reload":
            cmdargs = cmd[1] if len(cmd) > 1 else ''
            ctrlchan = bot.config['core']['ctrlchan']
            bot.reload_event.set()
            if reloader.do_reload(bot, ctrlchan, cmdargs, send):
                bot.server = init_server(bot)
                bot.reload_event.clear()
                send("Aye Aye Capt'n\n")
                bot.connection.privmsg(ctrlchan, "Aye Aye Capt'n (triggered from server)")
            self.request.close()
            return False
        elif cmd[0] == "raw":
            while cmd[0] != "endraw":
                send("ircbot-raw> ")
                cmd = self.get_data().strip()
                if cmd == "endraw":
                    return False
                bot.handler.connection.send_raw(cmd)
        elif cmd[0] == "quit":
            send("Goodbye.\n")
            self.request.close()
            return False
        else:
            send("Unknown command. Type help for more info.\n")
        return True

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
                    except BrokenPipeError:
                        # connection has been closed
                        return
                if not cmd:
                    continue
                if not self.handle_cmd(cmd, bot, send):
                    break
        except Exception as ex:
            msg, _ = backtrace.output_traceback(ex)
            ctrlchan = bot.config['core']['ctrlchan']
            send('%s\n' % msg)
            # If we've disconnected, there isn't much point sending errors to the network.
            if not isinstance(ex, client.ServerNotConnectedError):
                bot.connection.privmsg(ctrlchan, msg)
