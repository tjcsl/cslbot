# -*- coding: utf-8 -*-
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

from config import ADMINS, CHANNEL, NICK, LOGDIR
import re
import os
from glob import glob
from lxml.html import parse
from urllib.request import urlopen, Request
from urllib.error import URLError
import json
import importlib
import imp
import time
import socket


class MyHandler():
    def __init__(self):
        """ Set everything up.

        | ignored is a array of the nicks who are currently ignored for bot abuse.
        | logs is a dict containing a in-memory log for the primary channel as well as one for private messages.
        | channels is a dict containing the objects for each channel the bot is connected to.
        | abuselist is a dict keeping track of how many times nicks have used rate-limited commands.
        | modules is a dict containing the commands the bot supports.
        | scorefile is the fullpath to the file which records the scores.
        | logfiles is a dict containing the file objects to which the logs are written.
        """
        self.ignored = []
        self.logs = {CHANNEL: [], 'private': []}
        self.channels = {}
        self.abuselist = {}
        self.modules = self.loadmodules()
        self.scorefile = os.path.dirname(__file__)+'/score'
        self.logfiles = {CHANNEL: open("%s/%s.log" % (LOGDIR, CHANNEL), "a"),
                         'private': open("%s/private.log" % LOGDIR, "a")}

    def loadmodules(self):
        """ Load all the commands

        | globs over all the .py files in the commands dir.
        | skips file without the executable bit set
        | imports the modules into a dict
        """
        modulemap = {}
        for f in glob(os.path.dirname(__file__)+'/commands/*.py'):
            if os.access(f, os.X_OK):
                cmd = os.path.basename(f).split('.')[0]
                modulemap[cmd] = importlib.import_module("commands."+cmd)
        return modulemap

    def ignore(self, send, nick):
        """ Ignores a nick """
        if nick not in self.ignored:
            self.ignored.append(nick)
            send("Now ignoring %s." % nick)

    def abusecheck(self, send, nick, limit, msgtype):
        """ Rate-limits commands

        | if a nick uses commands with the limit attr set, record the time at which they were used
        | if the command is used more than *limit* times in a minute, ignore the nick
        """
        if nick not in self.abuselist:
            self.abuselist[nick] = [time.time()]
        else:
            self.abuselist[nick].append(time.time())
        count = 0
        for x in self.abuselist[nick]:
            # 60 seconds - arbitrary cuttoff
            if (time.time() - x) < 60:
                count = count + 1
        if count > limit and nick not in ADMINS:
            self.send(CHANNEL, nick, "\x02%s\x02 is a Bot Abuser." % nick, msgtype)
            self.ignore(send, nick)
            return True

    def privmsg(self, c, e):
        """ Handle private messages.

        Prevents users from changing scores in private.
        """
        nick = e.source.nick
        msg = e.arguments[0].strip()
        if re.search(r"([a-zA-Z0-9]+)(\+\+|--)", msg):
            self.send(nick, nick, 'Hey, no points in private messages!', e.type)
            return
        self.handle_msg('priv', c, e)

    def pubmsg(self, c, e):
        """ Handle public messages. """
        self.handle_msg('pub', c, e)

    def action(self, c, e):
        """ Handle actions. """
        self.handle_msg('action', c, e)

    def send(self, target, nick, msg, msgtype):
        """ Send a message

        Records the message in the log
        """
        self.do_log(target, nick, msg, msgtype)
        self.connection.privmsg(target, msg)

    def do_log(self, target, nick, msg, msgtype):
        """ Handles logging

        | logs nick and time
        | logs "New Day" when day turns over
        | logs both to a file and a in-memory array
        """
        if type(msg) != str:
            raise Exception("IRC doesn't like it when you send it a " + type(msg).__name__)
        if target[0] == "#":
            if target in self.channels and nick in self.channels[target].opers():
                    nick = '@' + nick
        else:
            target = 'private'
        currenttime = time.strftime('%H:%M:%S')
        day = int(time.strftime('%d'))
        if len(self.logs[target]) > 0:
            if day != self.logs[target][-1][0]:
                log = time.strftime('New Day: %a, %b %d, %Y\n')
                self.logs[target].append([day, log])
                self.logfiles[target].write(log)
                self.logfiles[target].flush()
        # strip ctrl chars from !creffett
        msg = msg.replace('\x02\x038,4', '<rage>')
        # strip non-printable chars
        msg = ''.join(c for c in msg if ord(c) > 31 and ord(c) < 127)
        if msgtype == 'action':
            log = '%s <%s> * %s %s\n' % (currenttime, nick, nick.replace('@', ''), msg)
        else:
            log = '%s <%s> %s\n' % (currenttime, nick, msg)
        self.logs[target].append([day, log])
        self.logfiles[target].write(log)
        self.logfiles[target].flush()

    def do_part(self, cmdargs, nick, target, msgtype, send, c):
        """ Leaves a channel

        | prevents user from leaving the primary channel
        """
        if not cmdargs:
            # don't leave the primary channel
            if target == CHANNEL:
                send("%s must have a home." % NICK)
                return
            else:
                cmdargs = target
        if cmdargs[0] != '#':
            cmdargs = '#' + cmdargs
        # don't leave the primary channel
        if cmdargs == CHANNEL:
            send("%s must have a home." % NICK)
            return
        self.send(cmdargs, nick, "Leaving at the request of " + nick, msgtype)
        c.part(cmdargs)

    def do_join(self, cmdargs, nick, msgtype, send, c):
        """ Join a channel

        | checks if bot is already joined to channel
        | opens logs for channel
        """
        if not cmdargs:
            return
        if cmdargs[0] != '#':
            cmdargs = '#' + cmdargs
        if cmdargs in self.channels:
            send("%s is already a member of %s" % (NICK, cmdargs))
            return
        c.join(cmdargs)
        self.logs[cmdargs] = []
        self.logfiles[cmdargs] = open("%s/%s.log" % (LOGDIR, cmdargs), "a")
        self.send(cmdargs, nick, "Joined at the request of " + nick, msgtype)

    def do_scores(self, matches, send, nick):
        """ Handles scores

        | If it's a ++ add one point unless the user is trying to promote themselves.
        | Else substract one point
        """
        for match in matches:
            name = match[0].lower()
            if match[1] == "++":
                score = 1
                if name == nick.lower():
                    send(nick + ": No self promotion! You lose 10 points.")
                    score = -10
            else:
                score = -1
            if os.path.isfile(self.scorefile):
                scores = json.load(open(self.scorefile))
            else:
                scores = {}
            if name in scores:
                scores[name] += score
            else:
                scores[name] = score
            f = open(self.scorefile, "w")
            json.dump(scores, f)
            f.write("\n")
            f.close()

    def do_urls(self, match, send):
        try:
            url = match.group(1)
            if not url.startswith('http'):
                url = 'http://' + url
            ret = lambda msg: msg
            shorturl = self.modules['short'].cmd(ret, url, {})
            # Wikipedia doesn't like the default User-Agent
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = parse(urlopen(req, timeout=5))
            title = html.find(".//title").text.strip()
            # strip unicode
            title = title.encode('utf-8', 'ignore').decode().replace('\n', ' ')
            send('** %s - %s' % (title, shorturl))
        except URLError as ex:
            # website does not exist
            if hasattr(ex.reason, 'errno') and ex.reason.errno == socket.EAI_NONAME:
                pass
            else:
                send('%s: %s' % (type(ex).__name__, str(ex).replace('\n', ' ')))
        # page does not contain a title
        except AttributeError:
            pass

    #FIXME: do some kind of mapping instead of a elif tree
    def handle_args(self, modargs, send, nick, target):
            args = {}
            for arg in modargs:
                if arg == 'channels':
                    args['channels'] = self.channels
                elif arg == 'connection':
                    args['connection'] = self.connection
                elif arg == 'nick':
                    args['nick'] = nick
                elif arg == 'modules':
                    args['modules'] = self.modules
                elif arg == 'scorefile':
                    args['scorefile'] = self.scorefile
                elif arg == 'logs':
                    args['logs'] = self.logs
                elif arg == 'target':
                    args['target'] = target if target[0] == "#" else "private"
                elif arg == 'ignore':
                    args['ignore'] = lambda nick: self.ignore(send, nick)
                else:
                    raise Exception("Invalid Argument: " + arg)
            return args

    def handle_msg(self, msgtype, c, e):
        if msgtype == 'action':
            nick = e.source.split('!')[0]
        else:
            nick = e.source.nick
        msg = e.arguments[0].strip()
        if msgtype == 'pub' or msgtype == 'action':
            target = e.target
        else:
            target = nick
        self.do_log(target, nick, msg, msgtype)
        send = lambda msg: self.send(target, NICK, msg, msgtype)
        if nick not in ADMINS and nick in self.ignored:
            return
        # SHUT CAPS LOCK OFF, MORON
        upper_count = 0
        lower_count = 0
        THRESHOLD = 0.65
        for i in msg:
            if i not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                lower_count += 1
            else:
                upper_count += 1
        upper_ratio = upper_count / len(msg)
        if upper_ratio > THRESHOLD and len(msg) > 6:
            c.send_raw("KICK %s %s :SHUT CAPS LOCK OFF, MORON" % (e.target, nick))
            return
        # is this a command?
        cmd = msg.split()[0]
        # handle !s/a/b/
        if cmd[:2] == '!s':
            cmd = cmd.split('/')[0]
        cmdargs = msg[len(cmd)+1:]
        if cmd[0] == '!':
            if cmd[1:] in self.modules:
                mod = self.modules[cmd[1:]]
                if hasattr(mod, 'limit') and self.abusecheck(send, nick, mod.limit, msgtype):
                    return
                args = self.handle_args(mod.args, send, nick, target) if hasattr(mod, 'args') else {}
                mod.cmd(send, cmdargs, args)
        #special commands
        if cmd[0] == '!':
            if cmd[1:] == 'reload':
                if cmdargs == 'pull':
                    self.modules['pull'].cmd(send, {}, {'nick': nick})
                send("Aye Aye Capt'n")
                for x in self.modules.values():
                    imp.reload(x)
            # everything below this point requires admin
            if nick in ADMINS:
                if cmd[1:] == 'cignore':
                    self.ignored = []
                    send("Ignore list cleared.")
                elif cmd[1:] == 'cabuse':
                    self.abuselist = {}
                    send("Abuse list cleared.")
                elif cmd[1:] == 'ignore':
                    self.ignore(send, cmdargs)
                elif cmd[1:] == 'showignore':
                    send(str(self.ignored))
                elif cmd[1:] == 'join':
                    self.do_join(cmdargs, nick, msgtype, send, c)
                elif cmd[1:] == 'part':
                    self.do_part(cmdargs, nick, target, msgtype, send, c)
        # ++ and --
        matches = re.findall(r"([a-zA-Z0-9]+)(\+\+|--)", msg)
        if matches:
            self.do_scores(matches, send, nick)

        # crazy regex to match urls
        match = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»....]))", msg)
        if match:
            self.do_urls(match, send)
  
