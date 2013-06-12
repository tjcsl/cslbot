def cmd(send, msg, args):
    if not msg:
        return
    msg = msg.replace(' ', '+')
    send('http://lmgtfy.com/?q=' + msg)
