from config import CHANNEL
from urllib.request import urlopen
from urllib.parse import urlencode
from lxml.html import parse


def cmd(e, c, msg):
        if not msg:
            return
        data = urlencode({'YodaMe': msg}).encode('UTF-8')
        html = urlopen("http://www.yodaspeak.co.uk/index.php", data, timeout=1)
        text = parse(html).find('//*[@id="result"]/div[1]/span/textarea').text
        c.privmsg(CHANNEL, text)
