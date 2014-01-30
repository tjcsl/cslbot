cslbot
======

A bot written by the TJHSST CSL for IRC. 



Documentation
-------------
See http://tjcsl.github.io/cslbot for api docs.

Setup
-----
Copy config.example to config.cfg and change values as needed.  
Install irc (https://pypi.python.org/pypi/irc),
beautiful soup (http://www.crummy.com/software/BeautifulSoup/)
lxml (https://pypi.python.org/pypi/lxml),
requests (https://pypi.python.org/pypi/requests),
and sqlalchemy (https://pypi.python.org/pypi/SQLAlchemy).
Python must be at least 3.3.

Adding Modules
--------------
To add a module place a <mod>.py file in the commands dir.  
The file must contain a method that is decorated with the @Command decorator;
this is used in the form ```@Command(['command_name_1', 'command_name_2'], ['arg_required_1', 'arg_required_2'])```.
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
Improved by bob_twinkles (Reed Koser, Class of 2015).  
Improved by csssuf.  
Improved by skasturi. (Srijay Kasturi)  
Criticized by creffett. (Chris Reffett, Class of 2011).
