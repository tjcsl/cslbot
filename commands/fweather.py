from config import CHANNEL
from urllib.request import urlopen
from bs4 import BeautifulSoup
import socket

def cmd(e, c, msg):
        html = urlopen('http://thefuckingweather.com/?where=' + msg.replace(' ', '%20'), timeout=5).read()
        soup = BeautifulSoup(html)
        temp, remark, flavor = soup.findAll('p')
        try:
            c.privmsg(CHANNEL, str(temp.contents[0].contents[0])  + ' F? ' + str(remark.contents[0]))
        except ValueError:
            c.privmsg(CHANNEL, 'No results for location ' + msg + '.')
        except socket.timeout:
            c.privmsg(CHANNEL, 'Connection timed out.')
