args = ['modules']


def cmd(send, msg, args):
    cmdlist = ' !'.join([x for x in sorted(args['modules'])])
    send('Commands: !' + cmdlist)
