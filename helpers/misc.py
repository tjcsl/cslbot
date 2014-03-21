# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi,
# Samuel Damashek, James Forcier, and Reed Koser
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

import subprocess
import re
from random import choice
from requests import get
from datetime import timedelta

_pinglist = {}


def check_exists(subreddit):
    req = get('http://www.reddit.com/r/%s/about.json' % subreddit, headers={'User-Agent': 'CslBot/1.0'}, allow_redirects=False)
    return req.status_code == 200


def parse_time(time):
    time, unit = time[:-1], time[-1].lower()
    if time.isdigit():
        time = int(time)
    else:
        return None
    conv = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    if unit in conv.keys():
        return time * conv[unit]
    else:
        return None if unit else time


def do_pull(srcdir, nick):
    # FIXME: Permissions hack.
    if nick == "msbobBot":
        subprocess.check_output(["sudo", "-n", "/home/peter/ircbot/scripts/fixperms.sh"], stderr=subprocess.STDOUT)
    return subprocess.check_output(['git', 'pull'], cwd=srcdir, stderr=subprocess.STDOUT).decode().splitlines()[-1]


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


#FIXME: there has to be a better way to do this.
def recordping(nick, channel):
    global _pinglist
    _pinglist[nick] = channel


def ping(c, e, pongtime):
    global _pinglist
    response = e.arguments[1].replace(' ', '.')
    nick = e.source.split('!')[0]
    try:
        pingtime = float(response)
        delta = timedelta(seconds=pongtime-pingtime)
        elapsed = "%s.%s seconds" % (delta.seconds, delta.microseconds)
    except ValueError:
        elapsed = response
    if nick in _pinglist:
        c.privmsg(_pinglist.pop(nick), "CTCP reply from %s: %s" % (nick, elapsed))
    else:
        c.privmsg(nick, "CTCP reply from %s: %s" % (nick, elapsed))


def get_channels(chanlist, nick):
    channels = []
    for name, channel in chanlist.items():
        if nick in channel.users():
            channels.append(name)
    return channels


def get_cmdchar(config, connection, msg, msgtype):
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
    preproc = subprocess.check_output(['gcc', '-include', '%s.h' % header, '-fdirectives-only', '-E', '-xc', '/dev/null'])
    if header == 'errno':
        defines = re.findall('^#define (E[A-Z]*) ([0-9]+)', preproc.decode(), re.MULTILINE)
    else:
        defines = re.findall('^#define (SIG[A-Z]*) ([0-9]+)', preproc.decode(), re.MULTILINE)
    deftoval = dict((x, y) for x, y in defines)
    valtodef = dict((y, x) for x, y in defines)
    if not msg:
        msg = choice(list(valtodef.keys()))
    if msg == 'list':
        return ", ".join(deftoval.keys())
    elif msg in deftoval:
        return '#define %s %s' % (msg, deftoval[msg])
    elif msg in valtodef:
        return '#define %s %s' % (valtodef[msg], msg)
    else:
        return "%s not found in errno.h" % msg
