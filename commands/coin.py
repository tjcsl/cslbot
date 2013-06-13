from random import randrange
def cmd(send, msg, args):
        coin = ['heads', 'tails']
        flip = str(coin[randrange(0, 1)])
        send('The coin lands on...' + flip + '.')
