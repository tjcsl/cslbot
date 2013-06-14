from urllib.parse import quote
from urllib.request import urlopen
import json


def cmd(send, msg, args):
    if not msg:
        return
    # pfoley's private key -- do not abuse
    key = 'AIzaSyAVcc0KavdZx_cfE1gtwMnsVudmJ5lvVMo'
    searchid = '011314769761209412182:6apbsde5g8e'
    data = json.loads(urlopen('https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s' % (key, searchid, quote(msg))).read().decode())
    try:
        url = data['items'][0]['link']
        send("Google says " + url)
    except KeyError:
        send("Google didn't say much")
