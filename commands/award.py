from random import choice


def cmd(send, msg, args):
        if not msg:
            return
        atype = choice(['gold', 'silver', 'bronze', 'platinum'])
        send(msg + ': I hereby award you this ' + atype + ' medal.')
