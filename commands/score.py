import re
from os.path import dirname
import json
from config import CHANNEL


def cmd(e, c, msg):
    match = re.match('([a-zA-Z0-9]+)', msg)
    try:
        data = json.load(open(dirname(__file__)+"/../score"))
        if match:
            name = match.group(1).lower()
            try:
                score = data[name]
                c.privmsg(CHANNEL,
                          "%s has %i points!" % (name, score))
            except:
                c.privmsg(CHANNEL, "Nobody cares about " + name)
        match = re.match('--(.*)', msg)
        if match:
            sorted_data = sorted(data, key=data.get)
            if match.group(1) == 'high':
                c.privmsg(CHANNEL, 'High Scores:')
                for x in range(1, 4):
                    name = sorted_data[-x]
                    c.privmsg(CHANNEL, "%s: %s" % (name, data[name]))
            if match.group(1) == 'low':
                c.privmsg(CHANNEL, 'Low Scores:')
                for x in range(0, 3):
                    name = sorted_data[x]
                    c.privmsg(CHANNEL, "%s: %s" % (name, data[name]))
    except OSError:
        c.privmsg(CHANNEL, "Nobody cares about anything.")
