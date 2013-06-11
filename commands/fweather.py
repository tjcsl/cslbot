from config import CHANNEL
from urllib.request import urlopen
from bs4 import BeautifulSoup

def cmd(e, c, msg):
        html = urlopen('http://thefuckingweather.com/?where=' + msg.replace(' ', '%20'), timeout=5).read()
        soup = BeautifulSoup(html)
        temp, remark, flavor = soup.findAll('p')
        c.privmsg(CHANNEL, str(temp.contents[0].contents[0])  + ' F? ' + str(remark.contents[0]))
