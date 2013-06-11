from config import CHANNEL
import urllib
import os
import re

def cmd(e, c, msg):
	url = urllib.quote(msg)
	f = os.popen('lynx --head --dump "http://www.google.com/search?q=%s&btnI=I%27m+Feeling+Lucky"' % url)
	output = f.read()
	location = re.findall(r"^Location:\s*(.+)")
	if location.length != 1 or "http://www.google.com" in location[0]:
		c.privmsg(CHANNEL, "Google didn't say much :(")
		return
	c.privmsg(CHANNEL, "Google says %s" % location[0])