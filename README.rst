======
CslBot
======

.. image:: https://travis-ci.org/tjcsl/cslbot.svg?branch=master
    :target: https://travis-ci.org/tjcsl/cslbot
    :alt: Travis CI

.. image:: https://codeclimate.com/github/tjcsl/cslbot/badges/gpa.svg
   :target: https://codeclimate.com/github/tjcsl/cslbot
   :alt: Code Climate

.. image:: https://coveralls.io/repos/tjcsl/cslbot/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/tjcsl/cslbot?branch=master
    :alt: Coverage
    
.. image:: https://readthedocs.org/projects/cslbot/badge/?version=latest
    :target: http://cslbot.readthedocs.org/en/latest
    :alt: Docs

A bot written by the TJHSST CSL for IRC. 

Support
-------
To quote the GPL: 

"This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."

That said, the bot devs hangout in #tjcsl-cslbot on freenode and are usually happy to answer your questions.

Documentation
-------------
See http://tjcsl.github.io/cslbot for api docs.

Changelog
---------
See https://github.com/tjcsl/cslbot/releases for the changelog.

Setup
-----
Run ./bot.py to setup the initial configuration and change values in config.cfg as needed.

You must copy static/groups.example to groups.cfg and make any needed changes to configure the commands and/or hooks you want.

If you want the tjhsst-specific commands, run `pip install git+git://github.com/tjcsl/cslbot-tjhsst` and add cslbot-tjhsst to extramodules.

Python must be at least 3.5.

Run `pip install .` to install the required libraries.

You must also install the appropriate DBAPI package as explained in the next section (unnecessary if you're using SQLite).

API Keys
--------

Wolfram Alpha: http://products.wolframalpha.com/api

Dictionary: http://dictionaryapi.com

Weather: http://www.wunderground.com/weather/api

Github: https://github.com/settings/tokens

FML: http://www.fmylife.com/api/home

Google: https://developers.google.com/url-shortener https://developers.google.com/custom-search/json-api/v1/overview

STANDS4 (zip code): http://www.abbreviations.com/apiuser.php

Note: you need to create a custom search app for xkcd.com to enable xkcd search as well as one for the whole internet to enable !google
This can be done at https://cse.google.com/cse/manage/all
Use the search engine IDs from this page with the api key from https://console.developers.google.com

Tumblr: http://www.tumblr.com/oauth/apps

Note: you need the OAuth consumer API key, consumer secret, OAuth token, and OAuth secret, which you can obtain via the Tumblr API console
at https://api.tumblr.com/console/calls/user/info. You can take the four keys listed in the sample code and put them into your config.cfg
in that order.

Service
-------
Note: the init script (scripts/ircbot) is gentoo/openrc specific.

Database Backends
-----------------
Example configurations:

1.  PostgreSQL - engine: postgresql://ircbot:dbpass@/dbname

2.  SQLite - engine: sqlite:///db.sqlite

3. MySQL/MariaDB - engine: mysql://ircbot:dbpass@/dbname

Note that for mysql you need to use the ROW_FORMAT=DYNAMIC option on the babble table.

This may require you to set innodb_file_format=Barracuda and innodb_large_prefix=on in my.cnf

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

Network type
------------
Different IRC networks use different software, such as atheme or UnrealIRCd. Certain details can vary between software, such as the method for
temporarily quieting users. You should set your network's type in config.cfg. The following values are supported:

* atheme (default)

* unreal

Services type
-------------
Services, such as NickServ and ChanServ, are generally independent of the network software. This can be set on the servicestype line in config.cfg.
The following values are supported:

* atheme (default)

* ircservices


Contributing
------------
Run flake8 --max-line-length 200 .

Run ./scripts/build_docs.sh

Run ./setup.py egg_info

Commit the changes.

Submit a PR and make sure the travis build is green.

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

Improved by wzhang (William Zhang, Class of 2018).
