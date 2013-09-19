# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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


def cmd(send, msg, args):
    """Converts text to morse code.
    Syntax: !morse <text>
    """
    morse_codes = {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.",
                   "g": "--.", "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..",
                   "m": "--", "n": "-.", "o": "---", "p": ".--.", "q": "--.-", "r": ".-.",
                   "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
                   "y": "-.--", "z": "--..", "1": ".----", "2": "..---", "3": "...--",
                   "4": "....-", "5": ".....", "6": "-....", "7": "--...", "8": "---..",
                   "9": "----.", "0": "-----", " ": "  ", ".": ".-.-.-", ",": "--..--",
                   "?": "..--..", "'": ".----.", "!": "-.-.--", "/": "-..-.", "(": "-.--.",
                   ")": "-.--.-", "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-",
                   "+": ".-.-.", "-": "-....-", "_": "..--.-", '"': ".-..-.", "$": "...-..-", "@": ".--.-."}
    morse = ""
    if not msg:
        send("morse what?")
        return
    for i in msg:
        try:
            morse += morse_codes[i.lower()] + " "
        except Exception:
            morse += "? "
    if len(morse) > 100:
        send("Your morse is too long. Have you considered Western Union?")
    else:
        send(morse)
