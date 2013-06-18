from random import choice


def cmd(send, msg, args):
    sayings = ['ic', '...']
    send(choice(sayings))
