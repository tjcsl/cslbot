#!/usr/bin/python
import logging
from oyoyo.client import IRCClient
from oyoyo import helpers
import handler

HOST = 'irc.freenode.net'
PORT = 6667
NICK = 'tjhsstBot'
CHANNELS = ['#tjhsst']
logging.basicConfig(level=logging.ERROR)


def connect_cb(cli):

    for i in CHANNELS:
        helpers.join(cli, i)


def main():
    logging.basicConfig(level=logging.DEBUG)

    cli = IRCClient(handler.MyHandler, host=HOST, port=PORT, nick=NICK,
                    connect_cb=connect_cb)
    conn = cli.connect()

    while True:
        next(conn)	   # python 3

if __name__ == '__main__':
    main()
