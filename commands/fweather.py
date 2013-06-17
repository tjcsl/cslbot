from urllib.request import urlopen
from bs4 import BeautifulSoup
import socket


def cmd(send, msg, args):
        try:
            html = urlopen('http://thefuckingweather.com/?where=' + msg.replace(' ', '%20'), timeout=5).read()
            soup = BeautifulSoup(html)
            temp, remark, flavor = soup.findAll('p')
            send((temp.contents[0].contents[0] + ' F? ' + remark.contents[0]).replace("UCKING", "!@#$%^"))
        except ValueError:
            send('NO !@#$%^& RESULTS.')
        except socket.timeout:
            send('CONNECTION TIMED THE !@#$ OUT.')
