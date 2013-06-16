args = ['nick', 'ignore']


def cmd(send, msg, args):
    if args['nick'] != 'creffett':
        send("You're not creffett!")
        args['ignore'](args['nick'])
        return
    if not msg:
        return
    creffett = '\x02\x038,4' + msg.upper() + "!!!"
    send(creffett)
    send('</rage>')
