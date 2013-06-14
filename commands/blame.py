from random import choice

args = ['channel']


def cmd(send, msg, args):
    user = choice(args['channel'].users())
    if msg:
        msg = " for " + msg
    send("I blame " + user + msg)
