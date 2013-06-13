def cmd(send, msg, args):
    if not msg:
        send("This tastes yummy!")
    else:
        msg.capitalize()
        send(msg + " tastes yummy!")
