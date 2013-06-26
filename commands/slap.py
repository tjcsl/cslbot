from config import NICK
args = ['nick', 'channels']

def cmd(send, msg, args):
    if not msg:
        users = args['channels'][CHANNEL].users()
        send(args['nick'] + ' slaps ' + choice(users))
        return
    else:
        send(args['nick'] + ' slaps ' + msg)
