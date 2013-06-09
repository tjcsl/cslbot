from config import CHANNEL, NICK


def cmd(c, msg):
    msg = msg.strip()
    if msg.lower() == NICK.lower():
        c.privmsg(CHANNEL, '%s is not feeling suicidal right now.' % msg)
    else:
        c.privmsg(CHANNEL, 'Die, %s!' % msg)
