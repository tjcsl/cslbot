import re

limit = 1


def cmd(send, msg, args):
        match = re.match('([a-zA-Z0-9]+) (.*)', msg)
        send("This command has been disabled due to abuse."); return;
        if match:
            message = match.group(2) + " "
            send('%s: %s' % (match.group(1), message * 3))
