import re
from random import choice
import json

args = ['scorefile']


def cmd(send, msg, args):
    try:
        data = json.load(open(args['scorefile']))
        match = re.match('([a-zA-Z0-9]+)', msg)
        if match:
            name = match.group(1).lower()
            try:
                score = data[name]
                send("%s has %i points!" % (name, score))
            except:
                send("Nobody cares about " + name)
        else:
            match = re.match('--(.*)', msg)
            if match:
                sorted_data = sorted(data, key=data.get)
                if match.group(1) == 'high':
                    send('High Scores:')
                    for x in [-1, -2, -3]:
                        try:
                            name = sorted_data[x]
                            send("%s: %s" % (name, data[name]))
                        except IndexError:
                            pass
                if match.group(1) == 'low':
                    send('Low Scores:')
                    for x in range(0, 3):
                        try:
                            name = sorted_data[x]
                            send("%s: %s" % (name, data[name]))
                        except IndexError:
                            pass
            else:
                name = choice(list(data.keys()))
                send("%s has %i points!" % (name, data[name]))
    except OSError:
        send("Nobody cares about anything.")
