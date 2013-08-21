from random import random
from random import choice
args = ['nick', 'channels', 'target', 'config']

def cmd(send, msg, args):
    """Generates a shibe reaction.
Syntax: !shibe <topic> or !shibe <topic1> <topic2>
"""
    topics = msg.split(' ')
    if topics.length == 1:
      topics.append(args['nick'])
    
    send('wow')
    
    if random() < 0.5:
      send('so' + topics[0])
      send('such' + topics[1])
    else:
      send('such' + topics[0])
      send('so' + topics[1])
    
    quotes = ['omg', 'amaze', 'nice']
    send(choice(quotes))
    
    send('wow')
    send('http://i.imgur.com/IEIMlEK.jpg')
