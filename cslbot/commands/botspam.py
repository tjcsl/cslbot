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
from ..helpers.misc import get_fortune
from ..helpers.textutils import gen_lenny
from ..helpers.web import get_urban


def gen_fortune(send):
    for line in get_fortune('-o').splitlines():
        send(line)


def gen_urban(send, session, key):
    defn, url = get_urban("", session, key)
    send(defn)
    if url:
        send("See full definition at %s" % url)


@Command('botspam', ['config', 'db'])
def cmd(send, _, args):
    """Abuses the bot.

    Syntax: {command}

    """

    def lenny_send(msg):
        send(gen_lenny(msg))

    key = args['config']['api']['bitlykey']
    cmds = [lambda: gen_fortune(lenny_send), lambda: gen_urban(lenny_send, args['db'], key)]
    choice(cmds)()
