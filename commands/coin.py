from random import choice


def cmd(send, msg, args):
    coin = ['heads', 'tails']
    if not msg:
        send('The coin lands on... ' + choice(coin) + '.')
    elif msg.isdigit():
        flips = []
        while int(msg) > len(flips):
            flips.append(choice(coin))
        send('The coins land on... ' + ', '.join(flips) + '.')
