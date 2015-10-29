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

from ..helpers import arguments
from ..helpers.web import get_urban
from ..helpers.orm import UrbanBlacklist
from ..helpers.command import Command


def blacklist_word(session, msg):
    if session.query(UrbanBlacklist).filter(UrbanBlacklist.word == msg).count():
        return "Word %s already blacklisted" % msg
    session.add(UrbanBlacklist(word=msg))
    return "Blacklisted word %s" % msg


def unblacklist_word(session, msg):
    term = session.query(UrbanBlacklist).filter(UrbanBlacklist.word == msg).first()
    if term is None:
        return "Word %s is not blacklisted" % msg
    session.delete(term)
    return "Removed blacklisting of word %s" % msg


@Command('urban', ['config', 'db', 'is_admin', 'nick'])
def cmd(send, msg, args):
    """Gets a definition from urban dictionary.
    Syntax: {command} [#<num>] <term>
    """
    key = args['config']['api']['googleapikey']
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--blacklist')
    parser.add_argument('--unblacklist')

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.blacklist:
        if args['is_admin'](args['nick']):
            send(blacklist_word(args['db'], cmdargs.blacklist))
        else:
            send("Blacklisting is admin-only")
    elif cmdargs.unblacklist:
        if args['is_admin'](args['nick']):
            send(unblacklist_word(args['db'], cmdargs.unblacklist))
        else:
            send("Unblacklisting is admin-only")
    else:
        defn, url = get_urban(msg, args['db'], key)
        send(defn)
        if url:
            send("See full definition at %s" % url)
