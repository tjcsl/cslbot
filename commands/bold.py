def cmd(send, msg, args):
    if not msg:
        return
    send('\x02' + msg)
