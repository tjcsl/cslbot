from config import CHANNEL
import re
from urllib.request import urlopen


def cmd(e, c, msg):
        url = urlopen('http://distrowatch.com/random.php', timeout=1).geturl()
        match = re.search('=(.*)', url)
        c.privmsg(CHANNEL, match.group(1))
