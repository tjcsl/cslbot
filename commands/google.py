from config import CHANNEL
import urllib.parse
import os
import re

def cmd(e, c, msg):
        url = urllib.parse.quote(msg)
        c.privmsg(CHANNEL, url)
        f = os.popen('lynx --head --dump "http://www.google.com/search?q=%s&btnI=I%%27m+Feeling+Lucky"' % url)
        output = f.read()
        location = re.findall(r"Location: (.+)", output)
        if len(location) != 1 or "http://www.google.com" in location[0]:
                c.privmsg(CHANNEL, "Google didn't say much :(")
        else:
                c.privmsg(CHANNEL, "Google says %s" % location[0])