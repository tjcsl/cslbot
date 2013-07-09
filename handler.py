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
from random import choice
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
        self.admins = {nick: False for nick in ADMINS}
        self.modules = self.loadmodules()
        self.scorefile = os.path.dirname(__file__)+'/score'
        self.logfiles = {CHANNEL: open("%s/%s.log" % (LOGDIR, CHANNEL), "a"),
                         'private': open("%s/private.log" % LOGDIR, "a")}
        self.caps = []
#       self.ctrlchan = "#fastbot-control"
        self.ctrlchan = "#" + NICK + "-control"
        self.kick_enabled = True

    def get_data(self):
        data = {}
        data['ignored'] = list(self.ignored)
        data['logs'] = dict(self.logs)
        data['logfiles'] = dict(self.logfiles)
        data['channels'] = dict(self.channels)
        data['abuselist'] = dict(self.abuselist)
        data['admins'] = dict(self.admins)
        return data

    def set_data(self, data):
        self.ignored = data['ignored']
        self.logs = data['logs']
        self.logfiles = data['logfiles']
        self.channels = data['channels']
        self.abuselist = data['abuselist']
        self.admins = data['admins']

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

    def is_admin(self, c, nick):
        if nick not in ADMINS:
            return False
        c.privmsg('NickServ', 'ACC ' + nick)
        if not self.admins[nick]:
            c.privmsg(CHANNEL, "Unverified admin: " + nick)
            return False
        else:
            return True

    def set_admin(self, e, c, send):
        match = re.match("(.*) ACC ([0-3])", e.arguments[0])
        if not match:
            return
        nick = e.source.nick
        if nick != 'NickServ':
            if nick in self.channels[CHANNEL].users():
                c.privmsg(CHANNEL, "Attemped admin abuse by " + nick)
                self.do_kick(c, e, send, nick, "imposter", 'private')
            return
        if int(match.group(2)) == 3:
            self.admins[match.group(1)] = True

    def get_admins(self, c):
        for admin in self.admins:
            c.privmsg('NickServ', 'ACC ' + admin)

    def abusecheck(self, send, nick, limit, msgtype, name):
        """ Rate-limits commands

        | if a nick uses commands with the limit attr set, record the time at which they were used
        | if the command is used more than *limit* times in a minute, ignore the nick
        """
        if nick not in self.abuselist:
            self.abuselist[nick] = {}
        if name not in self.abuselist[nick]:
            self.abuselist[nick][name] = [time.time()]
        else:
            self.abuselist[nick][name].append(time.time())
        count = 0
        for x in self.abuselist[nick][name]:
            # 60 seconds - arbitrary cuttoff
            if (time.time() - x) < 60:
                count = count + 1
        if count > limit:
            if name == 'scores':
                msg = self.modules['creffett'].gen_creffett("%s: don't abuse scores" % nick)
            else:
                msg = self.modules['creffett'].gen_creffett("%s: stop abusing the bot" % nick)
            self.send(CHANNEL, nick, msg, msgtype)
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

    def privnotice(self, c, e):
        """ Handle private notices. """
        self.handle_msg('privnotice', c, e)

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
            log = '%s * %s %s\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'nick':
            log = '%s -- %s is now known as %s\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'join':
            log = '%s %s has joined %s\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'part':
            log = '%s %s has left %s\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'quit':
            log = '%s %s has quit (%s)\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'kick':
            msg = msg.split(',')
            log = '%s %s has kicked %s (%s)\n' % (currenttime, nick.replace('@', ''), msg[0], msg[1])
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

    def do_scores(self, matches, send, msgtype, nick):
        """ Handles scores

        | If it's a ++ add one point unless the user is trying to promote themselves.
        | Else substract one point
        """
        for match in matches:
            name = match[0].lower()
            # limit to 5 score changes per minute
            if self.abusecheck(send, nick, 5, msgtype, 'scores'):
                return
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
            shorturl = self.modules['short'].get_short(url)
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

    def do_kick(self, c, e, send, nick, msg, msgtype):
        if not self.kick_enabled: return
        target = e.target if msgtype != 'private' else CHANNEL
        ops = self.channels[target].opers()
        if nick in self.caps:
            if NICK not in ops:
                c.privmsg(CHANNEL, self.modules['creffett'].gen_creffett("%s: /op the bot" % choice(ops)))
            else:
                c.kick(target, nick, self.modules['slogan'].gen_slogan(msg).upper())
                self.caps = [i for i in self.caps if i != nick]
        else:
            send("%s: warning, %s" % (nick, self.modules['slogan'].gen_slogan(msg).lower()))
            self.caps.append(nick)

    def do_caps(self, msg, c, e, nick, send):
        # SHUT CAPS LOCK OFF, MORON
        count = 0
        THRESHOLD = 0.65
        for i in msg:
            if i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                count += 1
        upper_ratio = count / len(msg)
        if upper_ratio > THRESHOLD and len(msg) > 6:
            self.do_kick(c, e, send, nick, "shutting caps lock off", 'pubmsg')

    #FIXME: do some kind of mapping instead of a elif tree
    def handle_args(self, modargs, send, nick, target, c):
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
                elif arg == 'admins':
                    args['admins'] = self.admins
                elif arg == 'is_admin':
                    args['is_admin'] = lambda nick: self.is_admin(c, nick)
                elif arg == 'target':
                    args['target'] = target if target[0] == "#" else "private"
                elif arg == 'ignore':
                    args['ignore'] = lambda nick: self.ignore(send, nick)
                else:
                    raise Exception("Invalid Argument: " + arg)
            return args
    
    def handle_ctrlchan(self, nick, msg, send, send_raw):
        cmd = msg.split()
        if cmd[0] == "quote":
            send_raw(" ".join(cmd[1:]))
        elif cmd[0] == "disable":
            if cmd[1] == "kick":
                self.kick_enabled = False
                send("Kick disabled.")
        elif cmd[0] == "enable":
            if cmd[1] == "kick":
                self.kick_enabled = True
                send("Kick enabled.")

    def handle_msg(self, msgtype, c, e):
        if e.target.lower() == self.ctrlchan.lower():
            self.handle_ctrlchan(e.source.nick, e.arguments[0].strip(), 
                    lambda msg: self.send(self.ctrlchan, NICK, msg, msgtype),
                    c.send_raw
                    )
        if msgtype == 'action':
            nick = e.source.split('!')[0]
        else:
            nick = e.source.nick
        msg = e.arguments[0].strip()
        if msgtype == 'pub' or msgtype == 'action':
            target = e.target
        else:
            target = nick
        send = lambda msg: self.send(target, NICK, msg, msgtype)
        if msgtype == 'privnotice':
            self.set_admin(e, c, send)
            return

        self.do_log(target, nick, msg, msgtype)

        if not self.is_admin(c, nick) and nick in self.ignored:
            return

        self.do_caps(msg, c, e, nick, send)

        # is this a command?
        cmd = msg.split()[0]
        # handle !s/a/b/
        if cmd[:2] == '!s':
            cmd = cmd.split('/')[0]
        cmdargs = msg[len(cmd)+1:]
        if cmd[0] == '!':
            if cmd[1:] in self.modules:
                mod = self.modules[cmd[1:]]
                if hasattr(mod, 'limit') and self.abusecheck(send, nick, mod.limit, msgtype, cmd[1:]):
                    return
                args = self.handle_args(mod.args, send, nick, target, c) if hasattr(mod, 'args') else {}
                mod.cmd(send, cmdargs, args)
        #special commands
        if cmd[0] == '!':
            # everything below this point requires admin
            if self.is_admin(c, nick):
                if cmd[1:] == 'cignore':
                    self.ignored = []
                    send("Ignore list cleared.")
                elif cmd[1:] == 'reload':
                    send("Aye Aye Capt'n")
                    for x in self.modules.values():
                        imp.reload(x)
                elif cmd[1:] == 'cabuse':
                    self.abuselist = {}
                    send("Abuse list cleared.")
                elif cmd[1:] == 'cadmin':
                    self.admins = {nick: False for nick in ADMINS}
                    self.get_admins(c)
                    send("Verified admins reset.")
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
            self.do_scores(matches, send, msgtype, nick)

        # crazy regex to match urls
        match = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»....]))", msg)
        if match:
            self.do_urls(match, send)

