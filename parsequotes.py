#!/usr/bin/python3 -OO
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek and James Forcier
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

import json
import argparse
from jinja2 import Environment, FileSystemLoader
from os.path import dirname, isfile


def main(outfile):
    filename = dirname(__file__) + "/data/quotes"
    if isfile(filename):
        quotes = json.load(open(filename))
    else:
        quotes = []
    quotes = [(i + " -- ").split("--") for i in quotes]
    output = ''
    env = Environment(loader=FileSystemLoader('static/templates'))
    output = env.get_template('quotes.html').render(quotes=quotes)
    open(outfile, 'w').write(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='The output file.')
    args = parser.parse_args()
    main(args.output)
