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

def check_quote_exists_by_id(cursor, qid):
    if (cursor.execute("SELECT count(id) FROM quotes WHERE id=?", (qid,)).fetchone()[0] == 0):
        return False
    return True

def do_usage(send):
    send("Usage: !quote <number>, !quote list, !quote add <quote> -- <nick>, !quote [remove|delete] <number>, !quote edit <number> <quote> -- <nick>")

def do_get_quote(num, cursor, send):
    quid = int(num)
    if not(check_quote_exists_by_id(cursor, qid)):
        send("That quote doesn't exist!")
        return
    quote = cursor.execute('SELECT nick,quote FROM quotes WHERE id=?', (qid,)).fetchone()
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

def do_update_quote(cursor, cmd, send): 
    #We need to strip off the 'edit ' but we don't want to split the quote into tiny little annoying peices
    cmd = cmd[len('edit '):]
    qid = cmd.split(' ')[0]
    if not qid.isdigit():
        send("The first argument to !quote edit must be a number!")
        return
    #and strip off the id of the quote we are editing
    cmd = cmd[len(qid)+1:]
    quote = cmd.split('--')
    #strip off excess leading/ending spaces
    quote = list(map (lambda x: x.strip(), quote))
    if not(check_quote_exists_by_id(cursor, qid)):
        send("That quote doesn't exist!")
        return
    cursor.execute('UPDATE quotes SET quote=?,nick=?', (quote[0],quote[1]))
    send ("Updated quote!")

def do_list_quotes(cursor, quote_url, send):
    cursor.execute("SELECT count(id) FROM quotes");
    send("There are " + str(cursor.fetchone()[0]) + " quotes. Check them out at " + quote_url)

def do_delete_quote(cursor, qid, send):
    if not qid.isdigit():
        send("Second argument to !quote remove must be a number!")
        return
    qid = int(qid)
    if not(check_quote_exists_by_id(cursor, qid)):
        send("That quote doesn't exist!")
        return
    cursor.execute("DELETE FROM quotes WHERE id=?", (qid,))
    send ('Deleted quote with ID ' + str(qid))


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
        do_list_quotes(cursor, args['config']['core']['quoteurl'], send)
    elif cmd[0] == 'remove' or cmd[0] == 'delete':
        if not(args['is_admin'](args['nick'])):
            send ("You aren't allowed to do delete quotes. Please ask a bot admin to do it")
            return
        do_delete_quote(cursor, cmd[1], send)
    elif cmd[0] == 'edit':
        do_update_quote(cursor, msg, send)
    elif cmd[0].isdigit():
        do_get_quote(cmd[1], cursor, send)
    else:
        do_usage(send)
