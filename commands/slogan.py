import re
from urllib.request import urlopen

limit = 5


def gen_slogan(msg):
        msg = msg.replace(' ', '%20')
        html = urlopen('http://www.sloganizer.net/en/outbound.php?slogan='
                       + msg, timeout=2).read().decode()
        return re.search('>(.*)<', html).group(1).replace('\\', '')


def cmd(send, msg, args):
    if not msg:
        return

    slogan = gen_slogan(msg)
    while not slogan:
        slogan = gen_slogan(msg)
    send(slogan)
