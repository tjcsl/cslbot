ircbot
======

The bot that inhabits the #tjhsst channel on freenode.


Setup
-----
Copy config.example to config.py and change values as needed.  
Install irc (https://pypi.python.org/pypi/irc) and lxml (https://pypi.python.org/pypi/lxml)

Adding Modules
--------------
To add a module place a <mod>.py file in the commands dir.  
The file must contain a def cmd(e, c, msg): method definition.  
The file will only be run if it is marked executable.


Steam
-----
*PLEASE NOTE!*  
The !steam command will not work without a valid Steam API key  
and a file steamids.py which contains a dictionary mapping username  
to STEAMID64. For this reason the !steam command is disabled by default;  
to re-enable it change STEAMENABLE to True in config.py and add your  
Steam API key as STEAMAPIKEY in config.py.

Credits
-------
Created by fwilson (Fox Wilson, Class of 2016).  
Improved by pfoley (Peter Foley, Class of 2013).  
Improved by sdamashek (Samuel Damashek, Class of 2017).  
Improved by csssuf (James Forcier, Class of 2014).  
Improved by TechFilmer.  
