import re
from config import CHANNEL


def cmd(e, c, msg):
        match = re.match('(.*) at (.*)', msg)
        if match:
            c.privmsg(CHANNEL, '%s has been thrown at %s'
                      % (match.group(1), match.group(2)))
