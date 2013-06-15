from random import choice


def cmd(send, msg, args):
    coin = ['heads', 'tails']
    if not msg:
        send('The coin lands on... ' + choice(coin) + '.')
    elif msg.isdigit():
        headFilps = 0
        tailFlips = 0
        flips = 0
        while int(msg) > flips:
            flip = choice(coin)
            flips = flips + 1
            if flip == 'heads':
                headFlips = headFlips + 1
            elif flip == 'tail':
                tailFlips = tailFlips + 1
        send('The coins land on heads ' + headFlips + ' times and on tails ' + tailFlips + ' times.')
