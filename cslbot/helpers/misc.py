# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import configparser
import logging
import os
import re
import subprocess
from datetime import datetime, timedelta
from os.path import exists, join
from random import choice, random
from typing import List, Tuple
from irc import client

import pkg_resources

from . import orm


def get_users(args):
    with args['handler'].data_lock:
        users = list(args['handler'].channels[args['target']].users()) if args['target'] != 'private' else ['you']
    return users


def parse_time(time):
    time, unit = time[:-1], time[-1].lower()
    if time.isdigit():
        time = int(time)
    else:
        return None
    conv = {
        's': 1,
        'm': 60,
        'h': timedelta(hours=1).total_seconds(),
        'd': timedelta(days=1).total_seconds(),
        'w': timedelta(weeks=1).total_seconds(),
        'y': timedelta(weeks=52).total_seconds()
    }
    if unit in conv.keys():
        return time * conv[unit]
    else:
        return None if unit else time


def do_pull(srcdir=None, repo=None):
    try:
        if repo is None:
            proc = subprocess.run(['git', 'pull'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, check=True)
            return proc.stdout.splitlines()[-1]
        else:
            proc = subprocess.run(
                ['pip', 'install', '--no-deps', '-U', 'git+git://github.com/%s' % repo],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=os.environ.copy(),
                universal_newlines=True,
                check=True)
            output = proc.stdout.splitlines()[-1]
            # Strip ascii color codes
            return re.sub(r'\x1b[^m]*h', '', output)
    except subprocess.CalledProcessError as e:
        for line in e.output.splitlines():
            logging.error(line)
        raise e


def do_nuke(c, nick, target, channel):
    c.privmsg(channel, "Please Stand By, Nuking " + target)
    c.privmsg_many([nick, target], "        ____________________         ")
    c.privmsg_many([nick, target], "     :-'     ,   '; .,   )  '-:      ")
    c.privmsg_many([nick, target], "    /    (          /   /      \\    ")
    c.privmsg_many([nick, target], "   /  ;'  \\   , .  /        )   \\  ")
    c.privmsg_many([nick, target], "  (  ( .   ., ;        ;  '    ; )   ")
    c.privmsg_many([nick, target], "   \\    ,---:----------:---,    /   ")
    c.privmsg_many([nick, target], "    '--'     \\ \\     / /    '--'   ")
    c.privmsg_many([nick, target], "              \\ \\   / /            ")
    c.privmsg_many([nick, target], "               \\     /              ")
    c.privmsg_many([nick, target], "               |  .  |               ")
    c.privmsg_many([nick, target], "               |, '; |               ")
    c.privmsg_many([nick, target], "               |  ,. |               ")
    c.privmsg_many([nick, target], "               | ., ;|               ")
    c.privmsg_many([nick, target], "               |:; ; |               ")
    c.privmsg_many([nick, target], "      ________/;';,.',\\ ________    ")
    c.privmsg_many([nick, target], "     (  ;' . ;';,.;', ;  ';  ;  )    ")


def ping(ping_map, c, e, pongtime):
    if e.arguments[1] == 'No such nick/channel':
        nick = e.arguments[0]
        if nick not in ping_map:
            return
        target = ping_map.pop(nick)
        c.privmsg(target, "%s: %s" % (e.arguments[1], e.arguments[0]))
        return
    nick = e.source.split('!')[0]
    response = e.arguments[1].replace(' ', '.')
    try:
        pingtime = float(response)
        delta = pongtime - datetime.fromtimestamp(pingtime)
        elapsed = "%s.%s seconds" % (delta.seconds, delta.microseconds)
    except (ValueError, OverflowError):
        elapsed = response
    target = ping_map.pop(nick) if nick in ping_map else nick
    c.privmsg(target, "CTCP reply from %s: %s" % (nick, elapsed))


def get_channels(chanlist, nick):
    channels = []
    for name, channel in chanlist.items():
        if nick in channel.users():
            channels.append(name)
    return channels


def get_cmdchar(config: configparser.ConfigParser, connection: client.ServerConnection, msg: str, msgtype: str) -> str:
    cmdchar = config['core']['cmdchar']
    botnick = '%s: ' % connection.real_nickname
    if msg.startswith(botnick):
        msg = msg.replace(botnick, cmdchar, 1)

    altchars = [x.strip() for x in config['core']['altcmdchars'].split(',')]
    if altchars and altchars[0] != '':
        for i in altchars:
            if msg.startswith(i):
                msg = msg.replace(i, cmdchar, 1)
    # Don't require cmdchar in PMs.
    if msgtype == 'privmsg' and not msg.startswith(cmdchar):
        msg = cmdchar + msg
    return msg


def parse_header(header, msg):
    proc = subprocess.run(
        ['gcc', '-include', '%s.h' % header, '-fdirectives-only', '-E', '-xc', '/dev/null'],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        check=True)
    if header == 'errno':
        defines = re.findall('^#define (E[A-Z]*) ([0-9]+)', proc.stdout, re.MULTILINE)
    else:
        defines = re.findall('^#define (SIG[A-Z]*) ([0-9]+)', proc.stdout, re.MULTILINE)
    deftoval = dict((x, y) for x, y in defines)
    valtodef = dict((y, x) for x, y in defines)
    if not msg:
        msg = choice(list(valtodef.keys()))
    if msg == 'list':
        return ", ".join(sorted(deftoval.keys()))
    elif msg in deftoval:
        return '#define %s %s' % (msg, deftoval[msg])
    elif msg in valtodef:
        return '#define %s %s' % (valtodef[msg], msg)
    else:
        return "%s not found in %s.h" % (msg, header)


def list_fortunes(offensive=False):
    cmd = ['fortune', '-f']
    if offensive:
        cmd.append('-o')
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, check=True)
    output = re.sub(r'[0-9]{1,2}\.[0-9]{2}%', '', proc.stdout)
    fortunes = [x.strip() for x in output.splitlines()[1:]]
    if offensive:
        fortunes = ['off/%s' % x for x in fortunes]
    return sorted(fortunes)


def get_fortune(msg, name='fortune'):
    fortunes = list_fortunes() + list_fortunes(True)
    cmd = ['fortune', '-s']
    match = re.match('(-[ao])( .+|$)', msg)
    if match:
        cmd.append(match.group(1))
        msg = match.group(2).strip()
    if 'bofh' in name or 'excuse' in name:
        if random() < 0.05:
            return "BOFH Excuse #1337:\nYou don't exist, go away!"
        cmd.append('bofh-excuses')
    elif msg in fortunes:
        cmd.append(msg)
    elif msg:
        return "%s is not a valid fortune module" % msg
    return subprocess.check_output(cmd).decode()


def ignore(session, nick):
    row = session.query(orm.Ignore).filter(orm.Ignore.nick == nick).first()
    if row is None:
        # FIXME: support expiration times for ignores
        session.add(orm.Ignore(nick=nick, expire=datetime.min))
        return "Now ignoring %s" % nick
    else:
        return "%s is already ignored." % nick


def get_version(srcdir):
    gitdir = join(srcdir, ".git")
    if not exists(gitdir):
        return None, pkg_resources.get_distribution('CslBot').version
    try:
        commit = subprocess.check_output(['git', '--git-dir=%s' % gitdir, 'rev-parse', 'HEAD']).decode().splitlines()[0]
        version = subprocess.check_output(['git', '--git-dir=%s' % gitdir, 'describe', '--tags']).decode().splitlines()[0]
        return commit, version
    except subprocess.CalledProcessError:
        return None, None


def split_msg(msgs: List[bytes], max_len: int) -> Tuple[str, List[bytes]]:
    """Splits as close to the end as possible."""
    msg = ""
    while len(msg.encode()) < max_len:
        if len(msg.encode()) + len(msgs[0]) > max_len:
            return msg, msgs
        char = msgs.pop(0).decode()
        # If we have a space within 15 chars of the length limit, split there to avoid words being broken up.
        if char == ' ' and len(msg.encode()) > max_len - 15:
            return msg, msgs
        msg += char
    return msg, msgs


def truncate_msg(msg: str, max_len: int) -> str:
    if len(msg.encode()) > max_len:
        msg_enc = [x.encode() for x in msg]
        msg, _ = split_msg(msg_enc, max_len - 3)
        return msg + "..."
    return msg


def escape(data):
    # handle arguments that end in '\', which is valid in irc, but causes issues with sql.
    return data.replace('\\', '\\\\')


def get_max_length(target: str, msgtype: str) -> int:
    overhead = r"PRIVMSG %s: \r\n" % target
    # FIXME: what the hell is up w/ message length limits?
    if msgtype == 'action':
        overhead += "\001ACTION \001"
        max_len = 454  # 512
    else:
        max_len = 453  # 512
    return max_len - len(overhead.encode())
