from helpers.command import Command

@Command('echo')
def cmd(send, msg, args):
    "Echos stuff"
    send(msg)
