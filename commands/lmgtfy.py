from config import CHANNEL


def cmd(e, c, msg):
        msg = msg.replace(' ', '+')
        c.privmsg(CHANNEL, 'http://lmgtfy.com/?q=' + msg)
