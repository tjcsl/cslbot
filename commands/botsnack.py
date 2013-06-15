from config import NICK


def cmd(send, msg, args):
    if not msg:
        send("This tastes yummy!")
    elif msg == NICK:
        send("Cannibalism is generally frowned upon.")
    else:
        send(msg.capitalize() + " tastes yummy!")
