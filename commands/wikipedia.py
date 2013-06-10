from config import CHANNEL


def cmd(c, msg):
        c.privmsg(CHANNEL, 'http://en.wikipedia.org/wiki/', msg)
