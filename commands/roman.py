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


def gen_roman(num):
    mapping = {1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X', 40: 'XL', 50: 'L', 90: 'XC', 100: 'C', 500: 'D', 900: 'CM', 1000: 'M'}
    if num >= 5000:
        return "If you want to deal with really big roman numerals, that's your problem."
    if num == 0:
        return "The romans didn't have zero, but you knew that, right?"
    if num in mapping.keys():
        return mapping[num]
    output = ""
    for k, v in reversed(sorted(mapping.items())):
        if num // k == 0:
            continue
        while num >= k:
            output += v
            num -= k
    return output


@Command('roman')
def cmd(send, msg, args):
    """Convert a number to the roman numeral equivalent.
    Syntax: !roman <number>
    """
    if not msg:
        send("What number?")
        return
    if not msg.isdigit():
        send("Invalid Number.")
        return
    send(gen_roman(int(msg)))
