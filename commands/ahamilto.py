from random import choice


def cmd(send, msg, args):
    sayings = ['ic', '...', 'ic...']
    send(choice(sayings))
