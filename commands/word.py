from config import CHANNEL
from urllib.request import urlopen


def cmd(e, c, msg):
        html = urlopen('http://randomword.setgetgo.com/get.php', timeout=1).read()
        # strip BOM
        c.privmsg(CHANNEL, html.decode()[1:].rstrip())
