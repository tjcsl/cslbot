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

args = ['db', 'nick', 'connection', 'is_admin', 'config']

def do_usage(send):
    send("Usage: !quote <number>, !quote list, !quote add <quote> -- <nick>, !quote [remove|delete] <number>, !quote edit <number> <quote> -- <nick>")

def do_get_quote(num, cursor, send):
    quid = int(num)
    quote = cursor.execute('SELECT nick,quote FROM quotes WHERE id=?', (qid,)).fetchone()
    if quote == None:
        send(num + " is not a valid quote number! Use !quote list to see valid quotes")
        return
    send(quote[1] + " -- " + quote[0])

def do_add_quote(cmd, cursor, send):
    #We need to strip off the 'add ' but we don't want to split the quote into tiny little annoying peices
    cmd = cmd[len('add '):]
    split = cmd.find('--')
    if split == -1:
        send("To add a quote, it must be in the format <quote> -- <nick>")
        return
    quote = cmd.split('--')
    #strip off excess leading/ending spaces
    quote = list(map (lambda x: x.strip(), quote))
    cursor.execute('INSERT INTO quotes(quote, nick, rowid) VALUES(?,?,NULL)', (quote[0], quote[1]))
    cursor.fetchone()
    send ("Added quote!")

def do_list_quotes(cursor, send):
    cursor.execute("SELECT id,quote,nick FROM quotes");
    send("List of quotes: ")
    for q in cursor:
        send(str(q[0]) + ":" + q[1] + " -- " + q[2])

def cmd(send, msg, args):
    """Handles quotes.
    Syntax: !quote <number>, !quote add <quote> -- <nick>, !quote list, !quote remove <number>, !quote edit <number> <quote> -- <nick>
    """
    cursor = args['db']
    cmd = msg.split(' ')
   
    print(msg)
    if len(cmd) < 1:
        do_usage(send)
    elif cmd[0] == 'add':
        do_add_quote(msg, cursor, send)
    elif cmd[0] == 'list':
        do_list_quotes(cursor, send)
    elif cmd[0] == 'remove' or cmd[0] == 'delete':
        if not(args['is_admin'](args['nick'])):
            send ("You aren't allowed to do delete quotes. Please ask a bot admin to do it")
            return
        send('That command isn\'t implemented yet!')
    elif cmd[0] == 'edit':
        send('That command isn\'t implemented yet!')
    elif cmd[0].isdigit():
        do_get_quote(cmd[1], cursor, send)
    else:
        do_usage(send)
