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

args = ['db', 'target', 'nick', 'config']


def get_log(cursor, user):
    if user is None:
        cursor.execute('SELECT msg,type,source FROM log ORDER BY time DESC LIMIT 50')
    else:
        cursor.execute('SELECT msg,type,source FROM log WHERE source=? ORDER BY time DESC LIMIT 50', (user,))
    # Don't parrot back the !s call.
    cursor.fetchone()
    return cursor.fetchall()


def get_modifiers(msg, nick):
    mods = {'ignorecase': False, 'allnicks': False, 'nick': nick}
    if not msg:
        return mods
    elif msg == "i":
        mods['ignorecase'] = True
    elif msg == "g":
        mods['allnicks'] = True
        mods['nick'] = None
    elif msg == "ig" or msg == "gi":
        mods['allnicks'] = True
        mods['ignorecase'] = True
        mods['nick'] = None
    else:
        mods['nick'] = msg
    return mods


def cmd(send, msg, args):
    """Corrects a previous message.
    Syntax: !s/<msg>/<replacement>/<ig|nick>
    """
    msg = msg.split('/')
    # not a valid sed statement.
    if not msg or len(msg) < 3:
        send("Invalid Syntax.")
        return
    if args['target'] == 'private':
        send("Don't worry, %s is not a grammar Nazi." % args['config']['core']['nick'])
        return
    string = msg[0]
    replacement = msg[1]
    modifiers = get_modifiers(msg[2], args['nick'])
    regex = re.compile(string, re.IGNORECASE) if modifiers['ignorecase'] else re.compile(string)
    log = get_log(args['db'], modifiers['nick'])

    for line in log:
        # ignore previous !s calls.
        if line['msg'].startswith('%ss/' % args['config']['core']['cmdchar']):
            continue
        if regex.search(line['msg']):
            output = regex.sub(replacement, line['msg'])
            if len(output) > 256:
                output = output[:253] + "..."
            if line['type'] == 'action':
                send("correction: * %s %s" % (line['source'], output))
            elif line['type'] != 'mode':
                send("%s actually meant: %s" % (line['source'], output))
            return
    send("No match found.")
