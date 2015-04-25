======
CslBot
======

.. image:: https://travis-ci.org/tjcsl/cslbot.svg?branch=master
    :target: https://travis-ci.org/tjcsl/cslbot

A bot written by the TJHSST CSL for IRC. 

Support
-------
To quote the GPL: 

"This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."

That said, the bot devs hangout in #tjcsl-cslbot on freenode and are usually happy to answer your questions.

Documentation
-------------
See http://tjcsl.github.io/cslbot for api docs.

Setup
-----
Run ./bot.py to setup the initial configuration and change values in config.cfg as needed.

You must copy helpers/groups.example to helpers/groups.cfg and make any needed changes to configure the commands and/or hooks you want.

If you want the tjhsst-specific commands, clone github.com/tjcsl/cslbot-tjhsst into commands/tjhsst and add it to extracommands.

Python must be at least 3.4.

Run `pip install -e .` to install the required libraries.

You must also install the appropriate DBAPI package as explained in the next section (unnecessary if you're using SQLite).

Service
-------
Note: the init script (scripts/ircbot) is gentoo/openrc specific.

Database Backends
-----------------
Example configurations:

1.  PostgreSQL - engine: postgresql://ircbot:dbpass@/dbname

2.  SQLite - engine: sqlite:///db.sqlite

See: http://docs.sqlalchemy.org/en/latest/core/engines.html for more information on SQLAlchemy database engine URLs.

Note that the primary install uses postgres, so sqlite and mysql receive less testing.

If you intend to use SQLite, the default DBAPI is provided by a built-in python module (sqlite3), so you don't need to install any additional packages.

If you intend to use PostgreSQL, the default DBAPI is provided by the psycopg2 package (https://pypi.python.org/pypi/psycopg2)

If you intend to use MySQL, the default DBAPI is provided by the mysql-python package (https://pypi.python.org/pypi/MySQL-python)

See the SQLAlchemy documentation if you want to use another backend.

Migrations
----------
You can run alembic -c config.cfg upgrade head at any time to ensure that you have the latest database migration.

Adding Modules
--------------
To add a module place a <mod>.py file in the commands directory.

The file must contain a method that is decorated with the @Command decorator;
this is used in the form ``@Command(['command_name_1', 'command_name_2'], ['arg_required_1', 'arg_required_2'])``.
The file will only be run if it is added to helpers/groups.cfg.

GeoIP
-----
To get GeoIP support, download the free database (in MMDB format) from http://dev.maxmind.com/geoip/geoip2/geolite2/.
You will then need to store the db at static/geoip.db.

parsedata.py
------------
This python script parses the db and generates jinja2-templated
html files containing quotes, score, polls, etc. It is intended to be used as a cronjob with
a webserver to serve quotes over HTTP.

parselogs.py
------------
This script parses the logs and generates human-readable logs for each channel the bot is in.
It is intended to be used as a cronjob to generate and optionally make available logs.

Credits
-------
Licensed under the GPL v2

This product may use GeoLite2 data created by MaxMind, available from http://www.maxmind.com.

Created by fwilson (Fox Wilson, Class of 2016).  

Rewritten by pfoley (Peter Foley, Class of 2013).  

Improved by sdamashek (Samuel Damashek, Class of 2017).  

Improved by bob_twinkles (Reed Koser, Class of 2015).  

Improved by csssuf.  

Improved by skasturi. (Srijay Kasturi)  

Criticized and subsequently improved by creffett. (Chris Reffett, Class of 2011).
