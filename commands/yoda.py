from config import CHANNEL
import urllib.request
import urllib.parse
import lxml.html


def cmd(c, msg):
        if not msg:
            return
        data = urllib.parse.urlencode({'YodaMe': msg}).encode('UTF-8')
        html = urllib.request.urlopen("http://www.yodaspeak.co.uk/index.php", data)
        text = lxml.html.parse(html).find('//*[@id="result"]/div[1]/span/textarea').text
        c.privmsg(CHANNEL, text)
