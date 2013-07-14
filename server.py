import threading
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
    threading.Thread(target=server.serve_forever, daemon=True).start()


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
            cmd = recv()
            if cmd == "help":
                send(HELP)
            elif cmd == "admins":
                admins = ", ".join(self.server.bot.handler.admins.keys())
                send(admins+'\n')
            elif cmd == "quit":
                send("Goodbye.\n")
                self.request.close()
                break
            else:
                send("Unknown command. Type help for more info.\n")
