from config import CHANNEL
import re
import urllib.request


def cmd(c, msg):
        html = urllib.request.urlopen('http://randomword.setgetgo.com/get.php).read().decode()
        match = re.search('>(.*)<', html)
        c.privmsg(CHANNEL, match.group(1))
