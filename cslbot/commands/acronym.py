# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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
from importlib import resources
from itertools import groupby
from random import choice

from ..helpers.command import Command


def get_list():
    # wordlist (COMMON.TXT) from http://www.gutenberg.org/ebooks/3201
    rawlist = sorted(resources.read_text('cslbot.static', 'wordlist').splitlines())
    words = {}
    for key, group in groupby(rawlist, key=lambda word: word[0].lower()):
        words[key] = list(group)
    return words


@Command("acronym")
def cmd(send, msg, _):
    """Generates a meaning for the specified acronym.

    Syntax: {command} <acronym>

    """
    if not msg:
        send("What acronym?")
        return
    words = get_list()
    letters = [c for c in msg.lower() if c in string.ascii_lowercase]
    output = " ".join([choice(words[c]) for c in letters])
    if output:
        send('%s: %s' % (msg, output.title()))
    else:
        send("No acronym found for %s" % msg)
