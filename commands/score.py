import re
import os
import json
from config import CHANNEL


def cmd(e, c, msg):
    match = re.match('([a-zA-Z0-9]+)', msg)
    if match:
        name = match.group(1).lower()
        try:
            score = json.load(open(os.path.dirname(__file__)+"/../score"))[name]
            c.privmsg(CHANNEL,
                      "%s has %i points!" % (name, score))
        except:
            c.privmsg(CHANNEL, "Nobody cares about " + name)
