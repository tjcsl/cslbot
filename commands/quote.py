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

from random import choice
from helpers.command import Command
from helpers.misc import check_quote_exists_by_id


def do_get_quote(cursor, qid=None):
    if qid is None:
        quotes = cursor.execute('SELECT quote,nick FROM quotes WHERE approved=1').fetchall()
        if not quotes:
            return "There aren't any quotes yet."
        quote = choice(quotes)
        return "%s -- %s" % (quote['quote'], quote['nick'])
    elif check_quote_exists_by_id(cursor, qid):
        quote = cursor.execute('SELECT nick,quote,approved FROM quotes WHERE id=?', (qid,)).fetchone()
        if int(quote['approved']) == 0:
            return "That quote hasn't been approved yet."
        else:
            return "%s -- %s" % (quote['quote'], quote['nick'])
    else:
        return "That quote doesn't exist!"


def get_quotes_nick(cursor, nick):
    rows = cursor.execute('SELECT quote FROM quotes WHERE nick=? AND approved=1', (nick,)).fetchall()
    if not rows:
        return "No quotes for %s" % nick
    quotes = [row['quote'] for row in rows]
    return "%s -- %s" % (choice(quotes), nick)


def do_add_quote(cmd, cursor, isadmin, send, args):
    if '--' not in cmd:
        send("To add a quote, it must be in the format <quote> -- <nick>")
        return
    quote = cmd.split('--')
    #strip off excess leading/ending spaces
    quote = [x.strip() for x in quote]
    cursor.execute('INSERT INTO quotes(quote, nick, submitter) VALUES(?,?,?)', (quote[0], quote[1], args['nick']))
    qid = cursor.lastrowid
    if isadmin:
        cursor.execute('UPDATE quotes SET approved=1 WHERE id=?', (qid,))
        send("Added quote %d!" % qid)
    else:
        send("Quote submitted for approval.", target=args['nick'])
        send("New Quote: #%d %s -- %s, Submitted by %s" % (qid, quote[0], quote[1], args['nick']), target=args['config']['core']['ctrlchan'])


def do_update_quote(cursor, qid, msg):
    if not qid.isdigit():
        return "The first argument to !quote edit must be a number!"
    if '--' not in msg:
        return "To add a quote, it must be in the format <quote> -- <nick>"
    quote = msg.split('--')
    #strip off excess leading/trailing spaces
    quote = [x.strip() for x in quote]
    if not check_quote_exists_by_id(cursor, qid):
        return "That quote doesn't exist!"
    cursor.execute('UPDATE quotes SET quote=?,nick=? WHERE id=?', (quote[0], quote[1], qid))
    return "Updated quote!"


def do_list_quotes(cursor, quote_url):
    cursor.execute("SELECT count(id) FROM quotes WHERE approved=1")
    num = cursor.fetchone()[0]
    return "There are %d quotes. Check them out at %squotes.html" % (num, quote_url)


def do_delete_quote(cursor, qid):
    if not qid.isdigit():
        return "Second argument to !quote remove must be a number!"
    qid = int(qid)
    if not check_quote_exists_by_id(cursor, qid):
        return "That quote doesn't exist!"
    cursor.execute("DELETE FROM quotes WHERE id=?", (qid,))
    return 'Deleted quote with ID %d' % qid


@Command('quote', ['db', 'nick', 'connection', 'is_admin', 'config', 'type'])
def cmd(send, msg, args):
    """Handles quotes.
    Syntax: !quote (number|nick), !quote add <quote> -- <nick>, !quote list, !quote remove <number>, !quote edit <number> <quote> -- <nick>
    """
    cursor = args['db']
    cmd = msg.split()
    isadmin = args['is_admin'](args['nick'])

    if not cmd:
        send(do_get_quote(cursor))
    elif cmd[0].isdigit():
        send(do_get_quote(cursor, int(cmd[0])))
    elif cmd[0] == 'add':
        if args['type'] == 'privmsg':
            send("You want everybody to know about your witty sayings, right?")
        else:
            msg = " ".join(cmd[1:])
            do_add_quote(msg, cursor, isadmin, send, args)
    elif cmd[0] == 'list':
        send(do_list_quotes(cursor, args['config']['core']['url']))
    elif cmd[0] == 'remove' or cmd[0] == 'delete':
        if isadmin:
            if len(cmd) == 1:
                send("Which quote?")
            else:
                send(do_delete_quote(cursor, cmd[1]))
        else:
            send("You aren't allowed to delete quotes. Please ask a bot admin to do it")
    elif cmd[0] == 'edit':
        if len(cmd) == 1:
            send("Which quote?")
        elif isadmin:
            msg = " ".join(cmd[2:])
            send(do_update_quote(cursor, cmd[1], msg))
        else:
            send("You aren't allowed to edit quotes. Please ask a bot admin to do it")
    else:
        send(get_quotes_nick(cursor, msg))
