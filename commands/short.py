import json
from urllib.request import urlopen, Request


def cmd(send, msg, args):
    if not msg:
        return
    data = {'longUrl': msg}
    data = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = Request('https://www.googleapis.com/urlshortener/v1/url', data, headers)
    rep = urlopen(req, timeout=1).read().decode()
    short = json.loads(rep)
    return send(short['id'])
