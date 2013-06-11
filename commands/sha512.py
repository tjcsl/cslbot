from config import CHANNEL
import hashlib


def cmd(e, c, msg):
        msg = msg.encode('utf-8')
        toSend = hashlib.sha512(msg).hexdigest()
        c.privmsg(CHANNEL, toSend)
