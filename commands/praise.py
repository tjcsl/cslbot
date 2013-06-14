import re
from urllib.request import urlopen


def cmd(send, msg, args):
        if not msg:
            return
        html = urlopen('http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG', timeout=1).read().decode()
        praise = re.search('h2>(.*)</h2', html, re.DOTALL).group(1).strip().replace('\n\n', '\n').replace('\n', ' ')
        send('%s: %s' % (msg, praise))
