from random import choice
from config import CHANNEL

args = ['channels']


def cmd(send, msg, args):
    #FIXME: blame people from the current channel
    users = args['channels'][CHANNEL].users()
    user = choice(users)
    if msg:
        msg = " for " + msg
    send("I blame " + user + msg)
