import hashlib


def cmd(send, msg, args):
        msg = msg.encode('utf-8')
        send(hashlib.sha512(msg).hexdigest())
