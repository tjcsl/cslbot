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
from helpers.orm import Quotes


def do_get_quote(session, qid=None):
    if qid is None:
        quotes = session.query(Quotes).filter(Quotes.approved == 1).all()
        if not quotes:
            return "There aren't any quotes yet."
        quote = choice(quotes)
        return "Quote #%d: %s -- %s" % (quote.id, quote.quote, quote.nick)
    else:
        quote = session.query(Quotes).get(qid)
        if quote is None:
            return "That quote doesn't exist!"
        if quote.approved == 0:
            return "That quote hasn't been approved yet."
        else:
            return "%s -- %s" % (quote.quote, quote.nick)


def get_quotes_nick(session, nick):
    rows = session.query(Quotes).filter(Quotes.nick == nick, Quotes.approved == 1).all()
    if not rows:
        return "No quotes for %s" % nick
    row = choice(rows)
    return "Quote #%d: %s -- %s" % (row.id, row.quote, nick)


def do_add_quote(cmd, session, isadmin, send, args):
    # FIXME: have better parsing.
    if '--' not in cmd:
        send("To add a quote, it must be in the format <quote> -- <nick>")
        return
    quote = cmd.split('--')
    # strip off excess leading/ending spaces
    quote = [x.strip() for x in quote]
    row = Quotes(quote=quote[0], nick=quote[1], submitter=args['nick'])
    session.add(row)
    session.flush()
    if isadmin:
        row.approved = 1
        send("Added quote %d!" % row.id)
    else:
        send("Quote submitted for approval.", target=args['nick'])
        send("New Quote: #%d %s -- %s, Submitted by %s" % (row.id, quote[0], quote[1], args['nick']), target=args['config']['core']['ctrlchan'])


def do_update_quote(session, qid, msg):
    if not qid.isdigit():
        return "The first argument to !quote edit must be a number!"
    if '--' not in msg:
        return "To add a quote, it must be in the format <quote> -- <nick>"
    quote = msg.split('--')
    # strip off excess leading/trailing spaces
    quote = [x.strip() for x in quote]
    row = session.query(Quotes).get(qid)
    if row is None:
        return "That quote doesn't exist!"
    row.update(quote=quote[0], nick=quote[1])
    return "Updated quote!"


def do_list_quotes(session, quote_url):
    num = session.query(Quotes).filter(Quotes.approved == 1).count()
    return "There are %d quotes. Check them out at %squotes.html" % (num, quote_url)


def do_delete_quote(session, qid):
    if not qid.isdigit():
        return "Second argument to !quote remove must be a number!"
    qid = int(qid)
    quote = session.query(Quotes).get(qid)
    if quote is None:
        return "That quote doesn't exist!"
    session.delete(quote)
    return 'Deleted quote with ID %d' % qid


@Command('quote', ['db', 'nick', 'is_admin', 'config', 'type'])
def cmd(send, msg, args):
    """Handles quotes.
    Syntax: !quote (number|nick), !quote add <quote> -- <nick>, !quote list, !quote remove <number>, !quote edit <number> <quote> -- <nick>
    """
    session = args['db']
    cmd = msg.split()
    isadmin = args['is_admin'](args['nick'])

    if not cmd:
        send(do_get_quote(session))
    elif cmd[0].isdigit():
        send(do_get_quote(session, int(cmd[0])))
    elif cmd[0] == 'add':
        if args['type'] == 'privmsg':
            send("You want everybody to know about your witty sayings, right?")
        else:
            msg = " ".join(cmd[1:])
            do_add_quote(msg, session, isadmin, send, args)
    elif cmd[0] == 'list':
        send(do_list_quotes(session, args['config']['core']['url']))
    elif cmd[0] == 'remove' or cmd[0] == 'delete':
        if isadmin:
            if len(cmd) == 1:
                send("Which quote?")
            else:
                send(do_delete_quote(session, cmd[1]))
        else:
            send("You aren't allowed to delete quotes. Please ask a bot admin to do it")
    elif cmd[0] == 'edit':
        if len(cmd) == 1:
            send("Which quote?")
        elif isadmin:
            msg = " ".join(cmd[2:])
            send(do_update_quote(session, cmd[1], msg))
        else:
            send("You aren't allowed to edit quotes. Please ask a bot admin to do it")
    else:
        send(get_quotes_nick(session, msg))
