import re
from urllib.request import urlopen


def cmd(send, msg, args):
        if not msg:
            return
        msg = msg.replace(' ', '%20')
        html = urlopen('http://www.sloganizer.net/en/outbound.php?slogan='
                       + msg, timeout=2).read().decode()
        slogan = re.search('>(.*)<', html).group(1).replace('\\', '')
        send(slogan)
