ircbot
======

The bot that inhabits the #tjhsst channel on freenode.



Documentation
-------------
See http://tjcsl.github.io/cslbot for api docs.

Setup
-----
Copy config.example to config.cfg and change values as needed.  
Install irc (https://pypi.python.org/pypi/irc), beautiful soup (http://www.crummy.com/software/BeautifulSoup/)
and lxml (https://pypi.python.org/pypi/lxml)

Adding Modules
--------------
To add a module place a <mod>.py file in the commands dir.  
The file must contain a def cmd(send, msg, args): method definition.  
The file will only be run if it is marked executable.


Steam
-----
*PLEASE NOTE!*  
The !steam command will not work without a valid Steam API key  
and a file steamids.pickle which contains a dictionary mapping username  
to STEAMID64. An example steamid mapping file is provided in the static folder.  
For this reason the !steam command is disabled by default;  
to re-enable it add your Steam API key as STEAMAPIKEY in config.py.

parsequotes.py
--------------

This python script parses the quotes stored and generates a jinja2-templated
html file containing the quotes. It is intended to be used as a cronjob with
a webserver to serve quotes over HTTP.

Credits
-------
Licensed under the GPL v2  
Created by fwilson (Fox Wilson, Class of 2016).  
Rewritten by pfoley (Peter Foley, Class of 2013).  
Improved by sdamashek (Samuel Damashek, Class of 2017).  
Improved by csssuf.  
Improved by skasturi. (Srijay Kasturi)  
Criticized by creffett. (Chris Reffett, Class of 2011).
