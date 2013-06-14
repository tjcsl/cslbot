import re
from urllib.request import urlopen


def cmd(send, msg, args):
        url = urlopen('http://distrowatch.com/random.php', timeout=1).geturl()
        match = re.search('=(.*)', url)
        send(match.group(1))
