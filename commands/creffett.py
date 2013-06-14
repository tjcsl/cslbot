limit = 2


def cmd(send, msg, args):
    if not msg:
        return
    creffett = '\x02\x038,4' + msg.upper() + "!!!"
    send(creffett)
    send('</rage>')
