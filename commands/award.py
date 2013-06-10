from config import CHANNEL


def cmd(c, msg):
        if not msg:
            return
        c.privmsg(CHANNEL, msg + ': I hearby award you this gold medal.')
