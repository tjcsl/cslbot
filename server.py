import socket
import threading
PORT = 2688
AUTH = "rightbracket@lexandria"
WELCOME = """
Welcome to the IRCbot console.
Copyright (c) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, and James Forcier.
Licensed under the GNU GPL version 2.

Type "help" for a list of commands.
"""
HELP = """
== IRCbot console commands list ==
help: show this help
quit: quit the console session
"""


def init_server(bot):
    BotnetServer(bot)


class BotnetServer:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.s = socket.socket()
        self.s.bind(('', PORT))
        self.s.listen(5)
        threading.Thread(target=self.accept_loop).start()

    def accept_loop(self):
        while True:
            conn, addr = self.s.accept()
            threading.Thread(target=self.handle_client,
                             args=[conn]).start()

    def handle_client(self, conn):
        conn.send("Password: ")
        pwd = conn.recv(1024).replace("\r\n", "")
        if pwd == AUTH:
            conn.send(WELCOME)
        else:
            conn.send("Incorrect password.\n")
            conn.close()
        done = False
        while not done:
            conn.send("ircbot> ")
            command = conn.recv(1024).replace("\r\n", "")
            #
            # Commands
            #
            if command == "quit":
                done = True
                conn.send("Goodbye.\n")
            elif command == "help":
                conn.send(HELP)
            #
            # End commands
            #
        conn.close()

BotnetServer(object)
