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

from os.path import basename

args = ['nick', 'target', 'ignore', 'connection', 'do_kick', 'kick_enabled', 'nick']


def gen_creffett(msg):
    return '\x02\x038,4' + msg.upper() + "!!!"


def cmd(send, msg, args):
    """RAGE!!!
    Syntax: !rage <text>
    """
    if 'creffett' in basename(__file__):
        if not args['nick'].startswith('creffett') and args['nick'] != args['config']['core']['nick']:
            send("You're not creffett!")
            args['ignore'](args['nick'])
            if args['target'] != 'private':
                args['do_kick'](args['target'], args['nick'], 'creffett impersonation')
            return
    if not msg:
        send("Rage about what?")
        return
    # c.send_raw("MODE %s -c" % CHANNEL)
    send(gen_creffett(msg))
    # c.send_raw("MODE %s +c" % CHANNEL)
    send('</rage>')
