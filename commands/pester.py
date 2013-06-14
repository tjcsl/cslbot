import re


def cmd(send, msg, args):
        match = re.match('([a-zA-Z0-9]+) (.*)', msg)
        if match:
            message = match.group(2) + " "
            send('%s: %s' % (match.group(1), message * 3))
