#!/usr/bin/python3 -OO
import logging
import traceback
import imp
import irc.bot
from config import CHANNEL, NICK, NICKPASS, HOST
from os.path import basename
import handler


class MyBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nick, nickpass, host, port=6667):
        if nickpass != '':
            server = irc.bot.ServerSpec(host, port, nickpass)
        else:
            server = irc.bot.ServerSpec(host, port)
        irc.bot.SingleServerIRCBot.__init__(self, [server], nick, nick)
        self.handler = handler.MyHandler()

    def on_welcome(self, c, e):
        logging.info("Connected to server " + HOST)
        self.handler.connection = c
        c.join(CHANNEL)

    def on_join(self, c, e):
        self.handler.channels[e.target] = self.channels[e.target]
        logging.info("Joined channel " + e.target)

    def on_part(self, c, e):
        del self.handler.channels[e.target]
        logging.info("Parted channel " + e.target)

    def handle_msg(self, msgtype, c, e):
        try:
            command = e.arguments[0].strip().split()[0]
            if command == '!reload':
                imp.reload(handler)
                # preserve log and ignored list
                log = list(self.handler.log)
                ignored = list(self.handler.ignored)
                channels = dict(self.handler.channels)
                self.handler = handler.MyHandler()
                self.handler.log = log
                self.handler.ignored = ignored
                self.handler.channels = channels
                self.handler.connection = c
            getattr(self.handler, msgtype)(c, e)
        except Exception as ex:
            trace = traceback.extract_tb(ex.__traceback__)[-1]
            trace = [basename(trace[0]), trace[1]]
            name = type(ex).__name__
            target = CHANNEL if msgtype == 'pubmsg' else e.source.nick
            c.privmsg(target, '%s in %s on line %s: %s' % (name, trace[0], trace[1], str(ex)))

    def on_pubmsg(self, c, e):
        self.handle_msg('pubmsg', c, e)

    def on_privmsg(self, c, e):
        self.handle_msg('privmsg', c, e)

    def get_version(self):
        return "Ircbot -- 1.0"


def main():
    logging.basicConfig(level=logging.INFO)
    bot = MyBot(CHANNEL, NICK, NICKPASS, HOST)
    bot.start()

if __name__ == '__main__':
    main()
