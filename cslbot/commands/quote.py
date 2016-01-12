# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
from random import choice
from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.orm import Quotes


def do_get_quote(session, qid=None):
    if qid is None:
        quotes = session.query(Quotes).filter(Quotes.accepted == 1).all()
        if not quotes:
            return "There aren't any quotes yet."
        quote = choice(quotes)
        return "Quote #%d: %s -- %s" % (quote.id, quote.quote, quote.nick)
    else:
        quote = session.query(Quotes).get(qid)
        if quote is None:
            return "That quote doesn't exist!"
        if quote.accepted == 0:
            return "That quote hasn't been accepted yet."
        else:
            return "%s -- %s" % (quote.quote, quote.nick)


def get_quotes_nick(session, nick):
    rows = session.query(Quotes).filter(Quotes.nick == nick, Quotes.accepted == 1).all()
    if not rows:
        return "No quotes for %s" % nick
    row = choice(rows)
    return "Quote #%d (out of %d): %s -- %s" % (row.id, len(rows), row.quote, nick)


def do_add_quote(nick, quote, session, isadmin, approve, send, args):
    row = Quotes(quote=quote, nick=nick, submitter=args['nick'])
    session.add(row)
    session.flush()
    if isadmin and approve:
        row.accepted = 1
        send("Added quote %d!" % row.id)
    else:
        if approve:
            send("Only admins can auto-approve quotes.")
        send("Quote submitted for approval.", target=args['nick'])
        send("New Quote: #%d %s -- %s, Submitted by %s" % (row.id, quote, nick, args['nick']), target=args['config']['core']['ctrlchan'])


def do_update_quote(session, qid, nick, quote):
    row = session.query(Quotes).get(qid)
    if row is None:
        return "That quote doesn't exist!"
    if quote:
        row.quote = " ".join(quote)
    if nick is not None:
        row.nick = nick
    return "Updated quote!"


def do_list_quotes(session, quote_url):
    num = session.query(Quotes).filter(Quotes.accepted == 1).count()
    return "There are %d quotes. Check them out at %squotes.html" % (num, quote_url)


def do_delete_quote(args, session, qid):
    if not args['is_admin'](args['nick']):
        return "You aren't allowed to delete quotes. Please ask a bot admin to do it"
    quote = session.query(Quotes).get(qid)
    if quote is None:
        return "That quote doesn't exist!"
    session.delete(quote)
    return 'Deleted quote with ID %d' % qid


def search_quote(session, offset, search):
    term = ' '.join(search)
    quote = session.query(Quotes).filter(Quotes.quote.ilike('%%%s%%' % term)).order_by(Quotes.id.desc()).offset(offset).first()
    if quote is None:
        return "No matching quote found."
    else:
        return "Quote #%d: %s -- %s" % (quote.id, quote.quote, quote.nick)


@Command('quote', ['db', 'nick', 'is_admin', 'config', 'type'])
def cmd(send, msg, args):
    """Handles quotes.
    Syntax: {command} <number|nick>, !quote --add <quote> --nick <nick> (--approve), !quote --list, !quote --delete <number>, !quote --edit <number> <quote> --nick <nick>
    !quote --search (--offset <num>) <number>
    """
    session = args['db']
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--approve', action='store_true')
    parser.add_argument('--nick', nargs='?')
    parser.add_argument('--offset', nargs='?', type=int, default=0)
    parser.add_argument('quote', nargs='*')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true')
    group.add_argument('--add', action='store_true')
    group.add_argument('--delete', '--remove', type=int)
    group.add_argument('--edit', type=int)
    group.add_argument('--search', nargs='*')

    if not msg:
        send(do_get_quote(session))
        return

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return

    if cmdargs.add:
        if args['type'] == 'privmsg':
            send("You want everybody to know about your witty sayings, right?")
        else:
            if cmdargs.nick is None:
                send('You must specify a nick.')
            elif not cmdargs.quote:
                send('You must specify a quote.')
            else:
                isadmin = args['is_admin'](args['nick'])
                do_add_quote(cmdargs.nick, " ".join(cmdargs.quote), session, isadmin, cmdargs.approve, send, args)
    elif cmdargs.list:
        send(do_list_quotes(session, args['config']['core']['url']))
    elif cmdargs.delete:
        send(do_delete_quote(args, session, cmdargs.delete))
    elif cmdargs.edit:
        if args['is_admin'](args['nick']):
            send(do_update_quote(session, cmdargs.edit, cmdargs.nick, cmdargs.quote))
        else:
            send("You aren't allowed to edit quotes. Please ask a bot admin to do it")
    elif cmdargs.search:
        send(search_quote(session, cmdargs.offset, cmdargs.search))
    else:
        if msg.isdigit():
            send(do_get_quote(session, int(msg)))
        else:
            if not re.match(args['config']['core']['nickregex'], msg):
                send('Invalid nick %s.' % msg)
            else:
                send(get_quotes_nick(session, msg))
