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

import re
from config import NICK
args = ['logs', 'target', 'nick']


def cmd(send, msg, args):
    msg = msg.split('/')
    # not a valid sed statement.
    if not msg or len(msg) < 3:
        return
    if args['target'] == 'private':
        send("Don't worry, %s is not a grammar Nazi." % NICK)
        return
    log = args['logs'][args['target']][:-1]
    string = msg[0]
    replacement = msg[1]
    if msg[2]:
        modifiers = msg[2].lower()
    else:
        modifiers = None
    regex = re.compile(string, re.IGNORECASE) if "i" in modifiers else re.compile(string)
    # search last 50 lines
    for line in reversed(log[-50:]):
        match = re.search("<@?(.*)> (.*)", line[1])
        action = False
        if not match:
            match = re.search(r" \* (.*?)\b (.*)", line[1])
            action = True
        try:
            user, text = match.groups()
        except AttributeError:
            continue
        # ignore stuff said by other people unless /g was passed
        if user != args['nick'] and "g" not in modifiers:
            continue
        # ignore previous !s commands
        if text[:2] == "!s":
            continue
        if regex.search(text):
            output = regex.sub(replacement, text)
            if action:
                send("correction: * %s %s" % (user, output))
            else:
                send("%s actually meant: %s" % (user, output))
            return
