bold = \u0002

def cmd(send, msg, args):
        msg = bold + msg + bold
        send(msg)
