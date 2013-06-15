from random import choice
coin = ['heads', 'tails']
flips = []


def cmd(send, msg, args):
        if not msg:
                send('The coin lands on...' + choice(coin) + '.')
        else:
                while msg < len(flips):
                        flips.append(choice(coin))
                send('The coins land on...' + flips + '.')
