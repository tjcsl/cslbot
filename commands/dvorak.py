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

from helpers.orm import Log
from helpers import arguments
from helpers.command import Command


def get_log(conn, user, target):
    query = conn.query(Log.msg).filter(Log.type == 'pubmsg', Log.target == target).order_by(Log.time.desc())
    if user is None:
        return query.offset(1).limit(1).scalar()
    else:
        return query.filter(Log.source == user).limit(1).scalar()


def translate(msg, encode=True):
    dv_orig = r'-=qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
    dv_dvor = r'[]\',.pyfgcrl/=\\aoeuidhtns-;qjkxbmwvz{}"<>PYFGCRL?+|AOEUIDHTNS_:QJKXBMWVZ'
    dv_encode = str.maketrans(dv_orig, dv_dvor)
    dv_decode = str.maketrans(dv_dvor, dv_orig)
    return msg.translate(dv_encode) if encode else msg.translate(dv_decode)


@Command(['dvorak', 'sdamashek'], ['db', 'config', 'target'])
def cmd(send, msg, args):
    """Converts a message to/from dvorak.
    Syntax: !dvorak <--nick <nick>|msg>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--nick', action=arguments.NickParser)
    parser.add_argument('msg', nargs='*')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if cmdargs.msg:
        if cmdargs.nick:
            send('--nick cannot be combined with a message')
        else:
            send(translate(" ".join(cmdargs.msg), False).strip())
    else:
        log = get_log(args['db'], cmdargs.nick, args['target'])
        if not log:
            send("Couldn't find a message from %s :(" % cmdargs.nick)
        else:
            send(translate(log))
