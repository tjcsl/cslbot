#!/usr/bin/python
import config
import logging
from oyoyo.client import IRCClient
from oyoyo import helpers
import handler

logging.basicConfig(level=logging.ERROR)


def connect_cb(cli):
    for i in config.CHANNELS:
        helpers.join(cli, i)


def main():
    logging.basicConfig(level=logging.DEBUG)

    cli = IRCClient(handler.MyHandler, host=config.HOST, port=config.PORT,
                    nick=config.NICK, connect_cb=connect_cb)
    conn = cli.connect()

    while True:
        next(conn)	   # python 3

if __name__ == '__main__':
    main()
