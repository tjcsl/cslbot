from config import CHANNEL


def cmd(c, msg):
        c.privmsg(CHANNEL, msg)
