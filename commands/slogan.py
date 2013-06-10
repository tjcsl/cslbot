from config import CHANNEL
import re
import urllib.request


def cmd(c, msg):
        if not msg:
            return
        msg = msg.replace(' ', '%20')
        html = urllib.request.urlopen('http://www.sloganizer.net/en/outbound.php?slogan=' + msg).read().decode()
        match = re.search('>(.*)<', html)
        c.privmsg(CHANNEL, match.group(1))
