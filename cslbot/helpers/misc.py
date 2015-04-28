# -*- coding: utf-8 -*-
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import json
import subprocess
import re
import pkg_resources
from os.path import exists, join
from random import choice, random
from datetime import timedelta
from simplejson import JSONDecodeError
from urllib.parse import unquote
from requests import post, get
from requests.exceptions import ReadTimeout
from . import orm, textutils


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


def do_pull(srcdir=None, repo=None):
    if repo is None:
        return subprocess.check_output(['git', 'pull'], cwd=srcdir, stderr=subprocess.STDOUT).decode().splitlines()[-1]
    else:
        return subprocess.check_output(['pip', 'install', '--no-deps', '-U', 'git+git://github.com/%s' % repo], stderr=subprocess.STDOUT).decode().splitlines()[-1]


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
        target = ping_map.pop(nick) if nick in ping_map else nick
        c.privmsg(target, "%s: %s" % (e.arguments[1], e.arguments[0]))
        return
    nick = e.source.split('!')[0]
    response = e.arguments[1].replace(' ', '.')
    try:
        pingtime = float(response)
        delta = timedelta(seconds=pongtime - pingtime)
        elapsed = "%s.%s seconds" % (delta.seconds, delta.microseconds)
    except ValueError:
        elapsed = response
    target = ping_map.pop(nick) if nick in ping_map else nick
    c.privmsg(target, "CTCP reply from %s: %s" % (nick, elapsed))


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


def ignore(session, nick):
    row = session.query(orm.Ignore).filter(orm.Ignore.nick == nick).first()
    if row is None:
        # FIXME: support expiration times for ignores
        session.add(orm.Ignore(nick=nick, expire=-1))
        return "Now ignoring %s" % nick
    else:
        return "%s is already ignored." % nick


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
    return ' '.join(output).strip()


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


def append_filters(filters):
    filter_list = []
    for next_filter in filter(None, filters.split(',')):
        if next_filter in textutils.output_filters.keys():
            filter_list.append(textutils.output_filters[next_filter])
        else:
            return None, "Invalid filter %s." % next_filter
    return filter_list, "Okay!"


def create_issue(title, desc, nick, repo, apikey):
    body = {"title": title, "body": "%s\nIssue created by %s" % (desc, nick), "labels": ["bot"]}
    headers = {'Authorization': 'token %s' % apikey}
    req = post('https://api.github.com/repos/%s/issues' % repo, headers=headers, data=json.dumps(body))
    data = req.json()
    if 'html_url' in data.keys():
        return data['html_url'], True
    elif 'message' in data.keys():
        return data['message'], False
    else:
        return "Unknown error", False
