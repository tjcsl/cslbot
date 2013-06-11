from config import CHANNEL
from urllib.parse import quote
from urllib.request import urlopen
import json


def cmd(e, c, msg):
        # pfoley's private key -- do not abuse
        key = 'AIzaSyAVcc0KavdZx_cfE1gtwMnsVudmJ5lvVMo'
        searchid = '011314769761209412182:6apbsde5g8e'
        data = json.loads(urlopen('https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s' % (key, searchid, quote(msg))).read().decode())
        try:
            url = data['items'][0]['link']
            c.privmsg(CHANNEL, "Google says " + url)
        except KeyError:
            c.privmsg(CHANNEL, "Google didn't say much")
