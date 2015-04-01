# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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

import argparse
from helpers.orm import Log
from helpers import arguments
from helpers.exception import NickException
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
    Syntax: !dvorak (--nick <nick>)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--nick', action=arguments.NickParser)
    parser.add_argument('msg', nargs='?', default=None)
    try:
        cmdargs = arguments.parse_args(parser, args['config'], msg)
    except NickException as e:
        send('%s is not a valid nick.' % e)
        return
    if cmdargs.msg and not cmdargs.nick:
        send(translate(msg, False).strip())
        return
    log = get_log(args['db'], cmdargs.nick, args['target'])
    if not log:
        send("Couldn't find a message from %s :(" % cmdargs.nick)
    else:
        send(translate(log))
