from config import CHANNEL
import re
from urllib.request import urlopen


def cmd(e, c, msg):
        if not msg:
            return
        msg = msg.replace(' ', '%20')
        html = urlopen('http://www.sloganizer.net/en/outbound.php?slogan='
                       + msg, timeout=1).read().decode()
        slogan = re.search('>(.*)<', html).group(1).replace('\\', '')
        c.privmsg(CHANNEL, slogan)
