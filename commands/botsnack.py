def cmd(send, msg, args):
    if not msg:
        send("This tastes yummy!")
    msg.title()
    send(msg + " tastes yummy!")
