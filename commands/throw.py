import re


def cmd(send, msg, args):
        match = re.match('(.*) at (.*)', msg)
        if match:
            send('%s has been thrown at %s' % (match.group(1), match.group(2)))
