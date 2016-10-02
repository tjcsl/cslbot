#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    long_description = f.read()

setup_requires = ['setuptools', 'setuptools_git']

setup(
    name="CslBot",
    description="An easily extensible, modular irc bot.",
    long_description=long_description,
    author="The TJHSST Computer Systems Lab",
    author_email="cslbot@pefoley.com",
    url="https://github.com/tjcsl/cslbot",
    version="0.21",
    license="GPL",
    zip_safe=False,
    packages=find_packages(exclude=['cslbot.tjhsst']),
    test_suite='test.test',
    package_data={
        '': [
            'alembic/env.py', 'alembic/script.py.mako', 'alembic/versions/*.py', 'static/*.example', 'static/slogans',
            'static/shakespeare-dictionary.json', 'static/wordlist', 'templates/sorttable.js', 'templates/*.html'
        ],
    },
    setup_requires=setup_requires,
    install_requires=setup_requires + [
        'SQLAlchemy>=1.0.0',  # bulk_insert_mappings
        'requests>=2.4.0',  # ConnectTimeout
        'alembic',
        'geoip2',
        'irc>=12.2',  # WHOX support
        'jinja2',
        'lxml',
        'python-dateutil',
        'simplejson',
        'requests_oauthlib',
        'sphinx>=1.4.8',  # search index fix
        'mypy-lang'
    ],
    extras_require={
        'analysis': ['flake8-debugger', 'flake8-import-order', 'flake8-string-format', 'flake8-coding', 'pep8-naming', 'radon', 'autopep8',
                     'docformatter'],
        'test': ['pytest-xdist'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
    keywords=['csl', 'tjhsst', 'tj', 'irc', 'bot'],
    entry_points={
        'console_scripts': [
            'cslbot = cslbot.helpers.core:init',
            'cslbot-parselogs = scripts.parselogs:main',
            'cslbot-parsedata = scripts.parsedata:main',
            'cslbot-genbabble = scripts.gen_babble:main',
            'cslbot-reload = scripts.reload:main',
            'cslbot-migrate = scripts.migrate:main',
        ]
    })
