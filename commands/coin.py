from random import choice


def cmd(send, msg, args):
    coin = ['heads', 'tails']
    if not msg:
        send('The coin lands on... ' + choice(coin) + '.')
    else:
        flips = 0
        headFlips = 0
        tailFlips = 0
        while int(msg) > flips:
            flip = choice(coin)
            flips = flips + 1
            if flip == 'heads':
                headFlips = headFlips + 1
            elif flip == 'tail':
                tailFlips = tailFlips + 1
        send('The coins land on heads ' + str(headFlips) + ' times and on tails ' + str(tailFlips) + ' times.')
