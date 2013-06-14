from urllib.request import urlopen

args = ['nick']


def cmd(send, msg, args):
    if not msg:
        return
    nick = args['nick']
    isup = urlopen("http://isup.me/%s" % msg.replace(' ', '%20')).read().decode('utf-8')
    if "looks down from here" in isup:
        send("%s: %s is down" % (nick, msg))
    elif "like a site on the interwho" in isup:
        send("%s: %s is not a valid url" % (nick, msg))
    else:
        send("%s: %s is up" % (nick, msg))
