# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Fox Wilson, Peter Foley, Srijay Kasturi,
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
from random import choice, random
from datetime import timedelta
from simplejson import JSONDecodeError
from urllib.parse import unquote
from requests import get
from requests.exceptions import ReadTimeout

_pinglist = {}


def check_exists(subreddit):
    req = get('http://www.reddit.com/r/%s/about.json' % subreddit, headers={'User-Agent': 'CslBot/1.0'})
    if req.json().get('kind') == 'Listing':
        # no subreddit exists, search results page is shown
        return False
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


# FIXME: there has to be a better way to do this.
def recordping(nick, channel):
    global _pinglist
    _pinglist[nick] = channel


def ping(c, e, pongtime):
    global _pinglist
    response = e.arguments[1].replace(' ', '.')
    nick = e.source.split('!')[0]
    try:
        pingtime = float(response)
        delta = timedelta(seconds=pongtime - pingtime)
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
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
    output = re.sub('[0-9]{1,2}\.[0-9]{2}%', '', output)
    fortunes = [x.strip() for x in output.splitlines()[1:]]
    if offensive:
        fortunes = map(lambda x: 'off/%s' % x, fortunes)
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


def get_rand_word():
    url = get('http://www.urbandictionary.com/random.php').url
    url = url.split('=')[1].replace('+', ' ')
    return unquote(url)


def get_urban(msg=""):
    if msg:
        output = get_urban_definition(msg)
    else:
        msg = get_rand_word()
        output = "%s: %s" % (msg, get_urban_definition(msg))
    return output


def get_urban_definition(msg):
    msg = msg.split()
    index = msg[0][1:] if msg[0].startswith('#') else None
    term = " ".join(msg[1:]) if index is not None else " ".join(msg)
    try:
        req = get('http://api.urbandictionary.com/v0/define', params={'term': term}, timeout=10)
        data = req.json()['list']
    except JSONDecodeError:
        return "UrbanDictionary is having problems."
    except ReadTimeout:
        return "UrbanDictionary timed out."
    if len(data) == 0:
        output = "UrbanDictionary doesn't have an answer for you."
    elif index is None:
        output = data[0]['definition']
    elif not index.isdigit() or int(index) > len(data) or int(index) == 0:
        output = "Invalid Index"
    else:
        output = data[int(index) - 1]['definition']
    output = output.splitlines()
    return ' '.join(output)
