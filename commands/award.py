from config import CHANNEL


def cmd(c, msg):
        c.privmsg(CHANNEL, msg +': I hearby award you this gold medal.')
