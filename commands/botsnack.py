def cmd(send, msg, args):
    if not msg:
        send("This tastes yummy!")
    else:
        send(msg.title() + " tastes yummy!")
