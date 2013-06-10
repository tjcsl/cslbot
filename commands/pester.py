import re
from config import CHANNEL


def cmd(c, msg):
        match = re.match('([a-zA-Z0-9]+) (.*)', msg)
        if match:
            message = match.group(2) + " "
            c.privmsg(CHANNEL, '%s: %s'
                      % (match.group(1), message * 3))
