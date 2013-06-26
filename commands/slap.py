from config import CHANNEL
from random import choice
args = ['nick', 'channels']


def cmd(send, msg, args):
    #FIXME: work in non-primary channels
    if not msg:
        users = args['channels'][CHANNEL].users()
        send(args['nick'] + ' slaps ' + choice(users))
        return
    else:
        send(args['nick'] + ' slaps ' + msg)
