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
from os.path import dirname, isfile


def main(template, outfile):
    filename = dirname(__file__) + "/data/quotes"
    if isfile(filename):
        quotes = json.load(open(filename))
    else:
        quotes = []
    output = ''
    for quote in quotes:
        output += "\t<tr>\n"
        quote = quote.split('--')
        text = quote[0]
        author = quote[1] if len(quote) > 1 else ''
        output += "\t\t<td>%s</td>\n" % text.strip()
        output += "\t\t<td>%s</td>\n" % author.strip()
        output += "\t</tr>\n"
    temp = open(template).read()
    temp = temp.replace('%REPLACEME%', output)
    open(outfile, 'w').write(temp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('template', help='The template file.')
    parser.add_argument('output', help='The output file.')
    args = parser.parse_args()
    main(args.template, args.output)
