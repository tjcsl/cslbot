import re
from urllib.request import urlopen

limit = 5


def gen_praise(msg):
    html = urlopen('http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG', timeout=1).read().decode()
    return re.search('h2>(.*)</h2', html, re.DOTALL).group(1).strip().replace('\n\n', '\n').replace('\n', ' ')
    return send('%s: %s' % (msg, praise))


def cmd(send, msg, args):
    if not msg:
        return
    praise = gen_praise(msg)
    while not praise:
        praise = gen_praise(msg)
    send(msg + ': ' + slogan)
