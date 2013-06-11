from config import CHANNEL


def cmd(e, c, msg):
        msg.replace(' ', '_')
        c.privmsg(CHANNEL, 'http://en.wikipedia.org/wiki/Special:Search/', msg)
