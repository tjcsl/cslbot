import sys
from config import ADMINS

args = ['nick', 'connection']


def cmd(send, msg, args):
    if args['nick'] not in ADMINS:
        send("Nope.")
    else:
        args['connection'].quit('Goodbye, Cruel World.')
        sys.exit(0)
