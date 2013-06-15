#!/usr/bin/python3 -OO
import logging
import imp
import irc.bot
from config import CHANNEL, NICK, NICKPASS, HOST
import handler
import time


class MyBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nick, nickpass, host, port=6667):
        if nickpass != '':
            server = irc.bot.ServerSpec(host, port, nickpass)
        else:
            server = irc.bot.ServerSpec(host, port)
        irc.bot.SingleServerIRCBot.__init__(self, [server], nick, nick)
        self.handler = handler.MyHandler()

    def on_welcome(self, c, e):
        logging.info("Connected to server")
        self.handler.connection = c
        c.join(CHANNEL)

    def on_join(self, c, e):
        logging.info("Joined channel")
        self.handler.channel = self.channels[CHANNEL]

    def on_part(self, c, e):
        logging.info("Parted channel")
        time.sleep(5)
        c.join(CHANNEL)

    def handle_msg(self, msgtype, c, e):
        try:
            command = e.arguments[0].strip().split()[0]
            if command == '!reload':
                imp.reload(handler)
                # preserve log
                log = list(self.handler.log)
                self.handler = handler.MyHandler()
                self.handler.log = log
                self.handler.channel = self.channels[CHANNEL]
                self.handler.connection = c
            getattr(self.handler, msgtype)(c, e)
        except Exception as ex:
            c.privmsg(CHANNEL, '%s: %s' % (type(ex), str(ex)))

    def on_pubmsg(self, c, e):
        self.handle_msg('pubmsg', c, e)

    def on_privmsg(self, c, e):
        self.handle_msg('privmsg', c, e)

    def get_version(self):
        return "Ircbot -- 1.0"


def main():
    bot = MyBot(CHANNEL, NICK, NICKPASS, HOST)
    bot.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
