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

from random import choice
from helpers.command import Command
from helpers.misc import get_fortune, get_urban


def gen_fortune(send):
    for line in get_fortune('-o').splitlines():
        send(line)


@Command('botspam')
def cmd(send, msg, args):
    """Abuses the bot.
    Syntax: !botspam
    """
    cmds = [lambda: gen_fortune(send),
            lambda: send(get_urban())]
    choice(cmds)()
