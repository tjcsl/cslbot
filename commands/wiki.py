import json
from urllib.request import urlopen
from urllib.parse import quote


def cmd(send, msg, args):
        html = urlopen('http://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srlimit=1&srsearch='+quote(msg))
        data = json.loads(html.read().decode())
        try:
            url = data['query']['search'][0]['title']
        except Exception:
            send("%s isn't important enough to have a wikipedia article." % msg)
            return
        url = url.replace(' ', '_')
        send('http://en.wikipedia.org/wiki/'+url)
