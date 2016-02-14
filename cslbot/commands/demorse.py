# -*- coding: utf-8 -*-
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

from ..helpers.command import Command


@Command('demorse')
def cmd(send, msg, _):
    """Converts morse to ascii.

    Syntax: {command} <text>

    """
    demorse_codes = {'.----': '1', '-.--': 'y', '..-': 'u', '...': 's',
                     '-.-.': 'c', '.-.-.': '+', '--..--': ',', '-.-': 'k',
                     '.--.': 'p', '----.': '9', '-----': '0', '  ': ' ',
                     '...--': '3', '-....-': '-', '...-..-': '$', '..---': '2',
                     '.--.-.': '@', '-...-': '=', '-....': '6', '...-': 'v',
                     '.----.': "'", '....': 'h', '.....': '5', '....-': '4',
                     '.': 'e', '.-.-.-': '.', '-': 't', '.-..': 'l', '..': 'i',
                     '.-': 'a', '-..-': 'x', '-...': 'b', '-.': 'n', '.-..-.': '"',
                     '.--': 'w', '-.--.-': ')', '--...': '7', '.-.': 'r',
                     '.---': 'j', '---..': '8', '--': 'm', '-.-.-.': ';',
                     '-.-.--': '!', '-..': 'd', '-.--.': '(', '..-.': 'f',
                     '---...': ':', '-..-.': '/', '..--.-': '_', '.-...': '&',
                     '..--..': '?', '--.': 'g', '--..': 'z', '--.-': 'q', '---': 'o'}
    demorse = ""
    if not msg:
        send("demorse what?")
        return
    for word in msg.lower().split("   "):
        for c in word.split():
            if c in demorse_codes:
                demorse += demorse_codes[c]
            else:
                demorse += "?"
        demorse += " "
    send(demorse)
