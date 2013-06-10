import re
import json
from config import CHANNEL


def cmd(c, msg):
    match = re.match('([a-zA-Z0-9]+)', msg)
    if match:
        name = match.group(1)
        try:
            score = json.load(open("score"))[name]
            c.privmsg(CHANNEL,
                      "%s has %i points!" % (name, score))
        except:
            c.privmsg(CHANNEL, "Nobody cares about " + name)
