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

import re
import os
import json
import importlib
import logging
import imp
import time
import socket
import string
from config import ADMINS, CHANNEL, CTRLCHAN, NICK, LOGDIR
from os.path import basename, dirname
from glob import glob
from lxml.html import parse
from urllib.request import urlopen, Request
from urllib.error import URLError
from random import choice, random


class BotHandler():
    def __init__(self):
        """ Set everything up.

        | kick_enabled controls whether the bot will kick people or not..
        | caps is a array of the nicks who have abused capslock.
        | ignored is a array of the nicks who are currently ignored for bot abuse.
        | disabled_mods is a array of the currently disabled modules.
        | logs is a dict containing a in-memory log for the primary channel, control channel, and private messages.
        | channels is a dict containing the objects for each channel the bot is connected to.
        | abuselist is a dict keeping track of how many times nicks have used rate-limited commands.
        | modules is a dict containing the commands the bot supports.
        | srcdir is the path to the directory where the bot is stored.
        | logfiles is a dict containing the file objects to which the logs are written.
        """
        self.kick_enabled = True
        self.caps = []
        self.ignored = []
        self.disabled_mods = []
        self.logs = {CHANNEL: [], CTRLCHAN: [], 'private': []}
        self.channels = {}
        self.abuselist = {}
        self.admins = {nick: False for nick in ADMINS}
        self.modules = self.loadmodules()
        self.srcdir = dirname(__file__)
        self.log_to_ctrlchan = False
        self.logfiles = {CHANNEL: open("%s/%s.log" % (LOGDIR, CHANNEL), "a"),
                         CTRLCHAN: open("%s/%s.log" % (LOGDIR, CTRLCHAN), "a"),
                         'private': open("%s/private.log" % LOGDIR, "a")}

    def get_data(self):
        """Saves the handler's data for :func:`bot.do_reload`"""
        data = {}
        data['caps'] = list(self.caps)
        data['ignored'] = list(self.ignored)
        data['disabled_mods'] = list(self.disabled_mods)
        data['logs'] = dict(self.logs)
        data['channels'] = dict(self.channels)
        data['abuselist'] = dict(self.abuselist)
        data['admins'] = dict(self.admins)
        data['logfiles'] = dict(self.logfiles)
        return data

    def set_data(self, data):
        """Called from :func:`bot.do_reload` to restore the handler's data."""
        self.caps = data['caps']
        self.ignored = data['ignored']
        self.disabled_mods = data['disabled_mods']
        self.logs = data['logs']
        self.logfiles = data['logfiles']
        self.channels = data['channels']
        self.abuselist = data['abuselist']
        self.admins = data['admins']

    def loadmodules(self):
        """Load all the commands.

        | Globs over all the .py files in the commands dir.
        | Skips file without the executable bit set
        | Imports the modules into a dict
        """
        modulemap = {}
        for f in glob(os.path.dirname(__file__)+'/commands/*.py'):
            if os.access(f, os.X_OK):
                cmd = basename(f).split('.')[0]
                modulemap[cmd] = importlib.import_module("commands."+cmd)
        return modulemap

    def ignore(self, send, nick):
        """Ignores a nick."""
        if nick not in self.ignored:
            self.ignored.append(nick)
            send("Now ignoring %s." % nick)

    def is_admin(self, c, nick, complain=True):
        """Checks if a nick is a admin.

        | If the nick is not in :const:`ADMINS` then it's not a admin.
        | If NickServ hasn't responded yet, then the admin is unverified, so assume they aren't a admin.
        """
        if nick not in ADMINS:
            return False
        c.privmsg('NickServ', 'ACC ' + nick)
        if not self.admins[nick]:
            if complain:
                c.privmsg(CHANNEL, "Unverified admin: " + nick)
            return False
        else:
            return True

    def set_admin(self, e, c, send):
        """Handle admin verification responses from NickServ.

        | If someone other than NickServ is trying to become a admin, kick them.
        | If NickServ tells us that the nick is authed, mark it as verified.
        """
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
        """Check verification for all admins."""
        for admin in self.admins:
            c.privmsg('NickServ', 'ACC ' + admin)

    def abusecheck(self, send, nick, limit, msgtype, cmd):
        """ Rate-limits commands.

        | If a nick uses commands with the limit attr set, record the time at which they were used.
        | If the command is used more than :data:`limit` times in a minute, ignore the nick.
        """
        if nick not in self.abuselist:
            self.abuselist[nick] = {}
        if cmd not in self.abuselist[nick]:
            self.abuselist[nick][cmd] = [time.time()]
        else:
            self.abuselist[nick][cmd].append(time.time())
        count = 0
        for x in self.abuselist[nick][cmd]:
            # 60 seconds - arbitrary cuttoff
            if (time.time() - x) < 60:
                count = count + 1
        if count > limit:
            if cmd == 'scores':
                msg = self.modules['creffett'].gen_creffett("%s: don't abuse scores" % nick)
            else:
                msg = self.modules['creffett'].gen_creffett("%s: stop abusing the bot" % nick)
            self.send(CHANNEL, nick, msg, msgtype)
            self.ignore(send, nick)
            return True

    def privmsg(self, c, e):
        """ Handle private messages.

        | Prevent users from changing scores in private.
        | Forward messages to :func:`handle_msg`.
        """
        nick = e.source.nick
        msg = e.arguments[0].strip()
        if re.search(r"([a-zA-Z0-9]+)(\+\+|--)", msg):
            self.send(nick, nick, 'Hey, no points in private messages!', e.type)
            return
        self.handle_msg('priv', c, e)

    def pubmsg(self, c, e):
        """ Handle public messages.

        Forward messages to :func:`handle_msg`.
        """
        self.handle_msg('pub', c, e)

    def privnotice(self, c, e):
        """ Handle private notices.

        Forward notices to :func:`handle_msg`.
        """
        self.handle_msg('privnotice', c, e)

    def action(self, c, e):
        """ Handle actions.

        Forward notices to :func:`handle_msg`.
        """
        self.handle_msg('action', c, e)

    def send(self, target, nick, msg, msgtype):
        """ Send a message.

        Records the message in the log.
        """
        self.do_log(target, nick, msg, msgtype)
        self.connection.privmsg(target, msg)

    def do_log(self, target, nick, msg, msgtype):
        """ Handles logging.

        | Logs nick and time.
        | Logs "New Day" when day turns over.
        | Logs both to a file and a in-memory array.
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
            log = '%s --> %s has joined %s\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'part':
            log = '%s <-- %s has left %s\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'quit':
            log = '%s <-- %s has quit (%s)\n' % (currenttime, nick.replace('@', ''), msg)
        elif msgtype == 'kick':
            msg = msg.split(',')
            log = '%s <-- %s has kicked %s (%s)\n' % (currenttime, nick.replace('@', ''), msg[0], msg[1])
        elif msgtype == 'mode':
            log = '%s -- Mode %s [%s] by %s\n' % (currenttime, target, msg, nick.replace('@', ''))
        else:
            log = '%s <%s> %s\n' % (currenttime, nick, msg)
        if self.log_to_ctrlchan:
            if target != CTRLCHAN:
                ctrlmsg = "(%s) %s" % (target, log)
                self.connection.privmsg(CTRLCHAN, ctrlmsg.strip())
        self.logs[target].append([day, log])
        self.logfiles[target].write(log)
        self.logfiles[target].flush()

    def do_part(self, cmdargs, nick, target, msgtype, send, c):
        """ Leaves a channel.

        Prevent user from leaving the primary channel.
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
        """ Join a channel.

        | Checks if bot is already joined to channel.
        | Opens logs for channel.
        """
        cmd = cmdargs.split()
        if not cmdargs:
            return
        if cmdargs[0] != '#':
            cmdargs = '#' + cmdargs
        if cmdargs in self.channels and len(cmd) > 0 and cmd[1] != "force":
            send("%s is already a member of %s" % (NICK, cmdargs))
            return
        c.join(cmd[0])
        self.logs[cmd[0]] = []
        self.logfiles[cmd[0]] = open("%s/%s.log" % (LOGDIR, cmd[0]), "a")
        self.send(cmd[0], nick, "Joined at the request of " + nick, msgtype)

    def do_scores(self, matches, send, msgtype, nick):
        """ Handles scores

        | If it's a ++ add one point unless the user is trying to promote themselves.
        | Otherwise substract one point.
        """
        scorefile = self.srcdir + '/score'
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
            if os.path.isfile(scorefile):
                scores = json.load(open(scorefile))
            else:
                scores = {}
            if name in scores:
                scores[name] += score
            else:
                scores[name] = score
            f = open(scorefile, "w")
            json.dump(scores, f)
            f.write("\n")
            f.close()

    def do_urls(self, match, send):
        """ Get titles for urls.

        | Generate a short url.
        | Get the page title.
        """
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
        """ Kick users.

        | If kick is disabled, don't do anything.
        | If the bot is not a op, rage at a op.
        | Kick the user.
        """
        if not self.kick_enabled:
            send("%s: you're lucky. kick is disabled." % nick)
            return
        target = e.target if msgtype != 'private' else CHANNEL
        ops = self.channels[target].opers()
        if NICK not in ops:
            c.privmsg(CHANNEL, self.modules['creffett'].gen_creffett("%s: /op the bot" % choice(ops)))
        else:
            c.kick(target, nick, self.modules['slogan'].gen_slogan(msg).upper())

    def do_caps(self, msg, c, e, nick, send):
        """ Check for capslock abuse.

        | Check if a line is more than :const:`THRESHOLD` percent uppercase.
        | If this is the first line, warn the user.
        | If this is the second line in a row, kick the user.
        """
        # SHUT CAPS LOCK OFF, MORON
        THRESHOLD = 0.65
        text = "shutting caps lock off"
        upper = [i for i in msg if i in string.ascii_uppercase]
        upper_ratio = len(upper) / len(msg)
        if upper_ratio > THRESHOLD and len(msg) > 6:
            if nick in self.caps:
                self.do_kick(c, e, send, nick, text, 'pubmsg')
                self.caps.remove(nick)
            else:
                send("%s: warning, %s would be a *really* good idea :)" % (nick, text))
                self.caps.append(nick)
        elif nick in self.caps:
            self.caps.remove(nick)

    def do_admin(self, c, cmd, cmdargs, send, nick, msgtype, target):
        if cmd == 'cignore':
            self.ignored = []
            send("Ignore list cleared.")
        elif cmd == 'cabuse':
            self.abuselist = {}
            send("Abuse list cleared.")
        elif cmd == 'cadmin':
            self.admins = {nick: False for nick in ADMINS}
            self.get_admins(c)
            send("Verified admins reset.")
        elif cmd == 'ignore':
            self.ignore(send, cmdargs)
        elif cmd == 'showignore':
            send(str(self.ignored))
        elif cmd == 'join':
            self.do_join(cmdargs, nick, msgtype, send, c)
        elif cmd == 'part':
            self.do_part(cmdargs, nick, target, msgtype, send, c)

    def do_band(self, msg, send):
        if ':' in msg:
            msg = msg.split(':')[1]
        if len(msg.split()) == 3 and random() < 0.05:
            send('"%s" would be a good name for a band...' % msg)

    def do_args(self, modargs, send, nick, target, c):
        """ Handle the various args that modules need."""
        realargs = {}
        args = {'nick': nick,
                'channels': self.channels,
                'connection': self.connection,
                'modules': self.modules,
                'srcdir': self.srcdir,
                'logs': self.logs,
                'admins': self.admins,
                'target': target if target[0] == "#" else "private",
                'do_log': lambda nick, msg, msgtype: self.do_log(target, nick, msg, msgtype),
                'is_admin': lambda nick: self.is_admin(c, nick),
                'ignore': lambda nick: self.ignore(send, nick)}
        for arg in modargs:
            if arg in args:
                realargs[arg] = args[arg]
            else:
                raise Exception("Invalid Argument: " + arg)
        return realargs

    def handle_ctrlchan(self, msg, c, send):
        """ Handle the control channel."""
        cmd = msg.split()
        if cmd[0] == "quote":
            c.send_raw(" ".join(cmd[1:]))
        elif cmd[0] == "cs" or cmd[0] == "chanserv":
            if cmd[1] == "op" or cmd[1] == "o":
                target = "OP %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
            elif cmd[1] == "deop" or cmd[1] == "do":
                target = "DEOP %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
            elif cmd[1] == "voice" or cmd[1] == "v":
                target = "VOICE %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
            elif cmd[1] == "devoice" or cmd[1] == "dv":
                target = "DEVOICE %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
            c.privmsg("ChanServ", target)
        elif cmd[0] == "disable":
            if cmd[1] == "kick":
                if not self.kick_enabled:
                    send("Kick already disabled.")
                else:
                    self.kick_enabled = False
                    send("Kick disabled.")
            elif cmd[1] == "module":
                if cmd[2] in self.disabled_mods:
                    send("Module already disabled.")
                else:
                    self.disabled_mods.append(cmd[2])
                    send("Module disabled.")
            elif cmd[1] == "logging":
                if logging.getLogger.getEffectiveLevel() == logging.INFO:
                    send("logging already disabled.")
                else:
                    logging.getLogger().setLevel(logging.INFO)
                    send("Logging disabled.")
            elif cmd[1] == "chanlog":
                if self.log_to_ctrlchan:
                    self.log_to_ctrlchan = False
                    send("Control channel logging disabled.")
                else:
                    send("Control channel logging is already disabled.")
        elif cmd[0] == "enable":
            if cmd[1] == "kick":
                if self.kick_enabled:
                    send("Kick already enabled.")
                else:
                    self.kick_enabled = True
                    send("Kick enabled.")
            elif cmd[1] == "module":
                if cmd[2] not in self.disabled_mods:
                    send("Module already enabled.")
                else:
                    self.disabled_mods.remove(cmd[2])
                    send("Module enabled.")
            elif cmd[1] == "all" and cmd[2] == "modules":
                self.disabled_mods = []
                send("Enabled all modules.")
            elif cmd[1] == "logging":
                logging.getLogger().setLevel(logging.DEBUG)
                send("Logging enabled.")
            elif cmd[1] == "chanlog":
                if not self.log_to_ctrlchan:
                    self.log_to_ctrlchan = True
                    send("Control channel logging enabled.")
                else:
                    send("Control channel logging is already enabled.")
        elif cmd[0] == "get":
            if cmd[1] == "disabled" and cmd[2] == "modules":
                mods = ", ".join(sorted(self.disabled_mods))
                if not mods:
                    send("No disabled modules.")
                send(mods)
            elif cmd[1] == "enabled" and cmd[2] == "modules":
                mods = ", ".join(sorted([i for i in self.modules if i not in self.disabled_mods]))
                send(mods)
        elif cmd[0] == "help":
            send("quote <raw command>")
            send("cs|chanserv <chanserv command>")
            send("disable|enable <kick|module <module>|logging|chanlog>")
            send("get <disabled|enabled> modules")

    def handle_msg(self, msgtype, c, e):
        """The Heart and Soul of IrcBot."""
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
        
        if "ACC" not in msg: #nasty hack to keep <nick> ACC 3 messages from nickserv out of the ctrl channel
            self.do_log(target, nick, msg, msgtype)

        if e.target == CTRLCHAN:
            self.handle_ctrlchan(msg, c, send)
        if msgtype == 'privnotice':
            self.set_admin(e, c, send)
            return

        if not self.is_admin(c, nick, False) and nick in self.ignored:
            return

        self.do_caps(msg, c, e, nick, send)
        self.do_band(msg, send)

        # is this a command?
        cmd = msg.split()[0]
        if cmd in self.disabled_mods or cmd[1:] in self.disabled_mods:
            send("That module is disabled, sorry.")
            return
        # handle !s/a/b/
        if cmd[:2] == '!s':
            cmd = cmd.split('/')[0]
        cmdargs = msg[len(cmd)+1:]
        found = False
        if cmd[0] == '!':
            if cmd[1:] in self.modules:
                mod = self.modules[cmd[1:]]
                if hasattr(mod, 'limit') and self.abusecheck(send, nick, mod.limit, msgtype, cmd[1:]):
                    return
                args = self.do_args(mod.args, send, nick, target, c) if hasattr(mod, 'args') else {}
                mod.cmd(send, cmdargs, args)
                found = True
        #special commands
        if cmd[0] == '!':
            if cmd[1:] == 'reload' and nick in ADMINS:
                found = True
                for x in self.modules.values():
                    imp.reload(x)
                send("Aye Aye Capt'n")
            # everything below this point requires admin
            if not found and self.is_admin(c, nick):
                self.do_admin(c, cmd[1:], cmdargs, send, nick, msgtype, target)
        # ++ and --
        matches = re.findall(r"([a-zA-Z0-9]+)(\+\+|--)", msg)
        if matches:
            self.do_scores(matches, send, msgtype, nick)

        # crazy regex to match urls
        match = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»....]))", msg)
        if match:
            self.do_urls(match, send)
