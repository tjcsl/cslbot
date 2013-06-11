import json
from config import CHANNEL
from urllib.request import urlopen


def cmd(e, c, msg):
        msg.replace(' ', '_')
        html = urlopen('http://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srlimit=1&srsearch='+msg)
        data = json.loads(html.read().decode())
        try:
            url = data['query']['search'][0]['title']
        except Exception:
            c.privmsg(CHANNEL, "%s isn't important enough to have a wikipedia article." % msg)
            return
        url = url.replace(' ', '_')
        c.privmsg(CHANNEL, 'http://en.wikipedia.org/wiki/'+url)
