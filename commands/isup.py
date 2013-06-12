from config import CHANNEL
from urllib.request import urlopen
from urllib.parse import quote

def cmd(e, c, msg):
	nick = e.source.nick
	isup = urlopen("http://isup.me/%s" % msg.replace(' ','%20')).read().decode('utf-8')
	if "looks down from here" in isup:
		c.privmsg(CHANNEL, "%s: %s is down" % (nick, msg))
	elif "like a site on the interwho" in isup:
		c.privmsg(CHANNEL, "%s: %s is not a valid url" % (nick, msg))
	else:
		c.privmsg(CHANNEL, "%s: %s is up" % (nick, msg))