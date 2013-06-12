def cmd(send, msg, args):
        if not msg:
            return
        send(msg + ': I hereby award you this gold medal.')
