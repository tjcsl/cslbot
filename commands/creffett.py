limit = 1


def cmd(send, msg, args):
    if not msg:
        return
    send('This command has been disabled due to abuse.')
