import socketserver

from . import core

def init_server(bot: core.IrcBot) -> BotNetServer:
    ...


class BotNetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    ...
