from config import CHANNEL
from urllib.request import urlopen


def cmd(c, msg):
        html = urlopen('http://randomword.setgetgo.com/get.php').read()
        # strip BOM
        c.privmsg(CHANNEL, html.decode()[1:].rstrip())
