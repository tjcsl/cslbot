import re
from config import NICK
args = ['logs', 'target', 'nick']


def cmd(send, msg, args):
    msg = msg.split('/')
    # not a valid sed statement.
    if not msg or len(msg) < 3:
        return
    if args['target'] == 'private':
        send("Don't worry, %s is not a grammar Nazi." % NICK)
        return
    log = args['logs'][args['target']][:-1]
    string = msg[0]
    replacement = msg[1]
    if msg[2] == "g":
        modifiers = msg[2]
    elif msg[2]:
        send("Unknown modifier " + msg[2])
        return
    else:
        modifiers = None
    # search last 50 lines
    for line in reversed(log[-50:]):
        match = re.search("<@?(.*)> (.*)", line[1])
        user, text = match.groups()
        # ignore stuff said by other people unless /g was passed
        if user != args['nick'] and not modifiers:
            continue
        if re.search(string, text):
            output = re.sub(string, replacement, text)
            send("%s actually meant: %s" % (user, output))
            return
