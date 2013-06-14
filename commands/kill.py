from config import NICK


def cmd(send, msg, args):
    if not msg:
        return
    if msg.lower() == NICK.lower():
        send('%s is not feeling suicidal right now.' % msg)
    else:
        send('Die, %s!' % msg)
