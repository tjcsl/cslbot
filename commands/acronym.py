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

from random import choice
from itertools import groupby

args = ['srcdir']


def get_list(srcdir):
    # wordlist (massaged COMMON.TXT) from http://www.gutenberg.org/ebooks/3201
    listfile = srcdir + '/static/words'
    rawlist = open(listfile).read()
    rawlist = sorted(rawlist.splitlines())
    words = {}
    for key, group in groupby(rawlist, key=lambda word: word[0].lower()):
        words[key] = list(group)
    return words

def cmd(send, msg, args):
    if not msg:
        return
    words = get_list(args['srcdir'])
    output = " ".join([choice(words[c]) for c in msg])
    send(msg + ': '+ output.title())
