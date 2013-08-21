from random import random, choice
args = ['nick']

def cmd(send, msg, args):
    """Generates a shibe reaction.
    Syntax: !shibe <topic> or !shibe <topic1> <topic2>
    """
    topics = msg.split(' ')
    if topics.length == 1:
        topics.append(args['nick'])
    send('wow')
    if random() < 0.5:
        send('        so' + topics[0])
        send('    such' + topics[1])
    else:
        send('        such' + topics[0])
        send('  so' + topics[1])
    
    quotes = ['omg', 'amaze', 'nice', 'clap']
    send(choice(quotes))
    send('           wow')
