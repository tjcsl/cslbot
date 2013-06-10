from config import CHANNEL


def cmd(e, c, msg):
        c.privmsg(CHANNEL, 'http://en.wikipedia.org/wiki/', msg)
