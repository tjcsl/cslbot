from random import choice
args = ['nick']

def cmd(send, msg, args):
    choices = msg.split(' ')
    action = ['draws a slip of paper from a hat and gets...', 'says enie, menie, miney, moe and chooses...']
    send(args['nick'] + choice(action) + choice(choices))
