# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

from helpers.command import Command


nato_codes = {"A": "Alpha", "B": "Bravo", "C": "Charlie", "D": "Delta",
              "E": "Echo", "F": "Foxtrot", "G": "Golf", "H": "Hotel",
              "I": "India", "J": "Juliet", "K": "Kilo", "L": "Lima",
              "M": "Mike", "N": "November", "O": "Oscar", "P": "Papa",
              "Q": "Quebec", "R": "Romeo", "S": "Sierra", "T": "Tango",
              "U": "Uniform", "V": "Victor", "W": "Whiskey", "X": "X-ray",
              "Y": "Yankee", "Z": "Zulu", " ": "Space", "1": "One",
              "2": "Two", "3": "Three", "4": "Four", "5": "Five", "6": "Six",
              "7": "Seven", "8": "Eight", "9": "Nine", "0": "Zero"}


def gen_nato(msg):
    nato = ""
    for x in msg:
        x = x.upper()
        if x in nato_codes:
            nato += "%s " % nato_codes[x]
        else:
            nato += "? "
    return nato


@Command(['nato', 'ipa'])
def cmd(send, msg, args):
    """Converts text into NATO form.
    Syntax: {command} <text>
    """
    if not msg:
        send("NATO what?")
        return
    nato = gen_nato(msg)
    if len(nato) > 100:
        send("Your NATO is too long. Have you considered letters?")
    else:
        send(nato)
