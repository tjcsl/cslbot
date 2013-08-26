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

import json
import os
from random import choice
from time import sleep

args = ['srcdir', 'nick', 'connection', 'is_admin']


def getquote(quotes, msg):
    if not quotes:
        return "Nobody has taste in this channel."
    elif not msg:
        return choice(quotes)
    elif not msg.isdigit():
        return "Not a Number"
    elif int(msg) >= len(quotes):
        return "Invalid quote number."
    else:
        return quotes[int(msg)]


def addquote(quotes, quotefile, quote):
    if not quote:
        return "No quote given."
    quotes += [quote]
    save_quotes(quotefile, quotes)
    return "Quote added successfully."


def listquotes(quotes, nick, c, send):
    if not quotes:
        send("Nobody has taste in this channel.")
    else:
        for i in enumerate(quotes):
            c.privmsg(nick, "%d: %s" % i)
            # work around broken clients.
            sleep(0.5)


def removequote(msg, quotes, quotefile):
    if not msg:
        return "Which quote?"
    if not msg.isdigit():
        return "Not A Valid Positive Integer."
    key = int(msg)
    if key >= len(quotes):
        return "Not a valid quote id."
    quotes.remove(quotes[key])
    save_quotes(quotefile, quotes)
    return "Deleted quote successfully."


def editquote(msg, quotes, quotefile):
    cmd = msg.split()
    if len(cmd) < 2:
        return "Missing arguments."
    if not cmd[0].isdigit():
        return "Not A Valid Positive Integer."
    key = int(cmd[0])
    if key >= len(quotes):
        return "Not a valid quote id."
    quotes[key] = " ".join(cmd[1:])
    save_quotes(quotefile, quotes)
    return "Edited quote successfully."


def save_quotes(quotefile, quotes):
    f = open(quotefile, "w")
    json.dump(quotes, f, indent=True, sort_keys=True)
    f.write("\n")
    f.close()


def cmd(send, msg, args):
    """Handles quotes.
    Syntax: !quote <number>, !quote add <quote>, !quote list, !quote remove <number>, !quote edit <number> <quote>
    """
    quotefile = args['srcdir'] + "/data/quotes"
    if os.path.isfile(quotefile):
        quotes = json.load(open(quotefile))
    else:
        quotes = []
    cmd = msg.split()
    if not cmd:
        send(getquote(quotes, msg))
    elif cmd[0] == "add":
        quote = " ".join(cmd[1:])
        send(addquote(quotes, quotefile, quote))
    elif cmd[0] == "list":
        listquotes(quotes, args['nick'], args['connection'], send)
    elif cmd[0] == "remove" or cmd[0] == "delete":
        if args['is_admin'](args['nick']):
            msg = " ".join(cmd[1:])
            send(removequote(msg, quotes, quotefile))
        else:
            send("Nope, not gonna do it.")
    elif cmd[0] == "edit":
        if args['is_admin'](args['nick']):
            msg = " ".join(cmd[1:])
            send(editquote(msg, quotes, quotefile))
        else:
            send("Nope, not gonna do it.")
    else:
        send(getquote(quotes, msg))
