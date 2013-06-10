from config import CHANNEL, NICK


def cmd(c, msg):
    if not msg:
        return
    if msg.lower() == NICK.lower():
        c.privmsg(CHANNEL, '%s is not feeling suicidal right now.' % msg)
    else:
        c.privmsg(CHANNEL, 'Die, %s!' % msg)
