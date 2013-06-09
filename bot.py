#!/usr/bin/python3 -OO
import config
import logging
from oyoyo.client import IRCClient
from oyoyo import helpers
import handler


def connect_cb(cli):
    for i in config.CHANNELS:
        helpers.join(cli, i)


def main():

    cli = IRCClient(handler.MyHandler, host=config.HOST, port=config.PORT,
                    nick=config.NICK, connect_cb=connect_cb)
    conn = cli.connect()

    while True:
        next(conn)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
