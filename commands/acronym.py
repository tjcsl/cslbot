# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import string
from helpers.command import Command
from random import choice
from itertools import groupby
from os.path import dirname


def get_list():
    # wordlist (COMMON.TXT) from http://www.gutenberg.org/ebooks/3201
    wordlist = dirname(__file__) + '/../static/wordlist'
    rawlist = open(wordlist).read()
    rawlist = sorted(rawlist.splitlines())
    words = {}
    for key, group in groupby(rawlist, key=lambda word: word[0].lower()):
        words[key] = list(group)
    return words


@Command("acronym")
def cmd(send, msg, args):
    """Generates a meaning for the specified acronym.
    Syntax: !acronym <acronym>
    """
    if not msg:
        send("What acronym?")
        return
    words = get_list()
    letters = [c for c in msg.lower() if c in string.ascii_lowercase]
    output = " ".join([choice(words[c]) for c in letters])
    if len(output) > 256:
        output = output[:253] + "..."
    send('%s: %s' % (msg, output.title()))
