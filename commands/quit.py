import sys
from config import CHANNEL, ADMINS


def cmd(e, c, msg):
    if e.source.nick not in ADMINS:
        c.privmsg(CHANNEL, "Nope.")
    else:
        c.quit('Goodbye, Cruel World.')
        sys.exit(0)
