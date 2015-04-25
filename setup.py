#!/usr/bin/env python3
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from setuptools import setup, find_packages
setup(
    name="CslBot",
    description="An easily extensible, modular irc bot.",
    author="The TJHSST Computer Systems Lab",
    author_email="cslbot@pefoley.com",
    url="https://github.com/tjcsl/cslbot",
    version="0.11",
    license="GPL",
    packages=find_packages(exclude=['commands.tjhsst']),
    test_suite='scripts.test',
    install_requires=[
        'SQLAlchemy>=1.0.0',
        'alembic',
        'beautifulsoup4',
        'geoip2',
        'irc',
        'lxml',
        'python-dateutil',
        'simplejson',
        ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3.4',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        ],
)
