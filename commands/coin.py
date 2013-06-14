from random import choice


def cmd(send, msg, args):
        coin = ['heads', 'tails']
        send('The coin lands on...' + choice(coin) + '.')
