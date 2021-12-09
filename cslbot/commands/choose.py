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

from random import choice

from ..helpers.command import Command


@Command('choose')
def cmd(send, msg, args):
    """Chooses between multiple choices.

    Syntax: {command} <object> or <object> (or <object>...)

    """
    if not msg:
        send("Choose what?")
        return
    choices = msg.split(' or ')
    action = [
        'draws a slip of paper from a hat and gets...', 'says eenie, menie, miney, moe and chooses...', 'picks a random number and gets...',
        'rolls dice and gets...', 'asks a random person and gets...', 'plays rock, paper, scissors, lizard, spock and gets...'
    ]
    send(f"{choice(action)} {choice(choices)}", 'action')
