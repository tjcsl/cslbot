# -*- coding: utf-8 -*-
# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi,
# Samuel Damashek and James Forcier
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

import re
import os
import json
import importlib
import imp
import time
import socket
import string
import errno
import control
from os.path import basename, dirname
from glob import glob
from lxml.html import parse
from urllib.request import urlopen, Request
from urllib.error import URLError
from random import choice, random
from sqlogger import Logger


class BotHandler():

    def __init__(self, config):
        """ Set everything up.

        | kick_enabled controls whether the bot will kick people or not..
        | caps is a array of the nicks who have abused capslock.
        | ignored is a array of the nicks who are currently ignored for
        |   bot abuse.
        | disabled_mods is a array of the currently disabled modules.
        | issues is a list keeping track of pending issues.
        | logs is a dict containing a in-memory log for the primary channel,
        |   control channel, and private messages.
        | channels is a dict containing the objects for each channel the bot
        |   is connected to.
        | abuselist is a dict keeping track of how many times nicks have used
        |   rate-limited commands.
        | modules is a dict containing the commands the bot supports.
        | srcdir is the path to the directory where the bot is stored.
        | logger - See logging.py, is a db wrapper for logging purposes
        |   written.
        """
        self.config = config
        self.guarded = []
        self.kick_enabled = True
        self.caps = []
        self.ignored = []
        self.disabled_mods = []
        self.issues = []
        self.logs = {config['core']['channel']: [],
                     config['core']['ctrlchan']: [],
                     'private': []}
        self.channels = {}
        self.abuselist = {}
        admins = config['auth']['admins'].split(', ')
        self.admins = {nick: False for nick in admins}
        self.modules = self.loadmodules()
        self.srcdir = dirname(__file__)
        self.log_to_ctrlchan = False
        self.logger = Logger(config['core']['logfile'])

    def get_data(self):
        """Saves the handler's data for :func:`bot.do_reload`"""
        data = {}
        data['caps'] = list(self.caps)
        data['ignored'] = list(self.ignored)
        data['disabled_mods'] = list(self.disabled_mods)
        data['issues'] = list(self.issues)
        data['logs'] = dict(self.logs)
        data['channels'] = dict(self.channels)
        data['abuselist'] = dict(self.abuselist)
        data['logger'] = dict(self.logger)
        data['guarded'] = list(self.guarded)
        return data

    def set_data(self, data):
        """Called from :func:`bot.do_reload` to restore the handler's data."""
        self.caps = data['caps']
        self.ignored = data['ignored']
        self.disabled_mods = data['disabled_mods']
        self.issues = data['issues']
        self.logs = data['logs']
        self.logger = data['logger']
        self.channels = data['channels']
        self.abuselist = data['abuselist']
        self.guarded = data['guarded']

    def loadmodules(self):
        """Load all the commands.

        | Globs over all the .py files in the commands dir.
        | Skips file without the executable bit set
        | Imports the modules into a dict
        """
        modulemap = {}
        for f in glob(os.path.dirname(__file__) + '/commands/*.py'):
            if os.access(f, os.X_OK):
                cmd = basename(f).split('.')[0]
                modulemap[cmd] = importlib.import_module("commands." + cmd)
        return modulemap

    def ignore(self, send, nick):
        """Ignores a nick."""
        if not nick:
            send("Ignore who?")
        elif nick not in self.ignored:
            self.ignored.append(nick)
            send("Now ignoring %s." % nick)

    def is_admin(self, c, nick, complain=True):
        """Checks if a nick is a admin.

        | If the nick is not in :const:`ADMINS` then it's not a admin.
        | If NickServ hasn't responded yet, then the admin is unverified,
        | so assume they aren't a admin.
        """
        if nick not in self.config['auth']['admins'].split(', '):
            return False
        c.privmsg('NickServ', 'ACC ' + nick)
        if not self.admins[nick]:
            if complain:
                c.privmsg(self.config['core']['channel'],
                          "Unverified admin: " + nick)
            return False
        else:
            return True

    def set_admin(self, c, msg, send, nick, target):
        """Handle admin verification responses from NickServ.

        | If someone other than NickServ is trying to become a admin,
        | kick them.
        | If NickServ tells us that the nick is authed, mark it as verified.
        """
        match = re.match("(.*) ACC ([0-3])", msg)
        if not match:
            return
        if nick != 'NickServ':
            if nick in list(self.channels[self.config['core']['channel']]
                            .users()):
                c.privmsg(self.config['core']['channel'],
                          "Attemped admin abuse by " + nick)
                self.do_kick(c, send, target, nick, "imposter")
            return
        if int(match.group(2)) == 3:
            self.admins[match.group(1)] = True

    def get_admins(self, c):
        """Check verification for all admins."""
        for admin in self.admins:
            c.privmsg('NickServ', 'ACC ' + admin)

    def abusecheck(self, send, nick, limit, msgtype, cmd):
        """ Rate-limits commands.

        | If a nick uses commands with the limit attr set, record the time
        | at which they were used.
        | If the command is used more than :data:`limit` times in a
        | minute, ignore the nick.
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
            self.send(self.config['core']['channel'], nick, msg, msgtype)
            self.ignore(send, nick)
            return True

    def privmsg(self, c, e):
        """ Handle private messages.

        | Prevent users from changing scores in private.
        | Forward messages to :func:`handle_msg`.
        """
        nick = e.source.nick
        msg = e.arguments[0].strip()
        cmdchar = self.config['core']['cmdchar']
        botnick = '%s: ' % self.config['core']['nick']
        if msg.startswith(botnick):
            msg = msg.replace(botnick, self.config['core']['cmdchar'])
        if msg.startswith('%sissue' % cmdchar):
            self.send(nick, nick, 'You want to let everybody know about your problems, right?', e.type)
            return
        elif msg.startswith('%sgcc' % cmdchar):
            self.send(nick, nick, 'GCC is a group excercise!', e.type)
            return
        elif re.search(r"([a-zA-Z0-9]+)(\+\+|--)", msg):
            self.send(nick, nick, 'Hey, no points in private messages!',
                      e.type)
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

    def mode(self, c, e):
        """ Handle actions.

        Forward notices to :func:`handle_msg`.
        """
        self.handle_msg('mode', c, e)

    def send(self, target, nick, msg, msgtype):
        """ Send a message.

        Records the message in the log.
        """
        msgs = []

        while len(msg) > 400:
            split_pos = self.get_split_pos(msg)
            msgs.append(msg[:split_pos].strip())
            msg = msg[split_pos:]
        msgs.append(msg.strip())
        for i in msgs:
            self.do_log(target, nick, i, msgtype)
            if msgtype == 'action':
                self.connection.action(target, i)
            else:
                self.connection.privmsg(target, i)

    def get_split_pos(self, message):
        """Gets the proper split position at or around position 400 of
           a message."""
        for i in range(385, 415):
            if message[i] == ' ':
                return i
        return 400

    def do_log(self, target, nick, msg, msgtype):
        """ Handles logging.

        | Logs nick and time.
        | Logs "New Day" when day turns over.
        | Logs both to a file and a in-memory array.
        """
        if not isinstance(msg, str):
            raise Exception("IRC doesn't like it when you send it a " +
                            type(msg).__name__)
        target = target.lower()
        isop = False
        if target[0] == "#":
            if target in self.channels and nick in \
                    self.channels[target].opers():
                    isop = True
        else:
            target = 'private'
        currenttime = time.strftime('%H:%M:%S')
        day = int(time.strftime('%d'))
        if len(self.logs[target]) > 0:
            if day != self.logs[target][-1][0]:
                log = time.strftime('New Day: %a, %b %d, %Y\n')
                self.logs[target].append([day, log])
                #TODO: Log datetime changes
        # strip ctrl chars from !creffett
        msg = msg.replace('\x02\x038,4', '<rage>')
        # strip non-printable chars
        msg = ''.join(c for c in msg if ord(c) > 31 and ord(c) < 127)
        #TODO: We need to implement the following in the log generation script:
        # -action
        # -nick
        # -join
        # -part
        # -quit
        # -kick
        # -mode
        # -pub
        # -private
        #log to sqlite logger
        self.logger.log(target, nick, msg, msgtype)
        
        if self.log_to_ctrlchan:
            ctrlchan = self.config['core']['ctrlchan']
            if target != ctrlchan:
                ctrlmsg = "(%s) %s" % (target, log)
                self.connection.privmsg(ctrlchan, ctrlmsg.strip())
        self.logs[target].append([day, log])

    def do_part(self, cmdargs, nick, target, msgtype, send, c):
        """ Leaves a channel.

        Prevent user from leaving the primary channel.
        """
        channel = self.config['core']['channel']
        botnick = self.config['core']['nick']
        if not cmdargs:
            # don't leave the primary channel
            if target == channel:
                send("%s must have a home." % botnick)
                return
            else:
                cmdargs = target
        if cmdargs[0] != '#':
            cmdargs = '#' + cmdargs
        # don't leave the primary channel
        if cmdargs == channel:
            send("%s must have a home." % botnick)
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
        if cmdargs in self.channels and len(cmd) > 1 and cmd[1] != "force":
            send("%s is already a member of %s" % (self.config['core']['nick'],
                 cmdargs))
            return
        c.join(cmd[0])
        self.logs[cmd[0]] = []
        self.logfiles[cmd[0]] = open("%s/%s.log" % (self.config['core']['logdir'],
                                     cmd[0]), "a")
        self.send(cmd[0], nick, "Joined at the request of " + nick, msgtype)

    def do_scores(self, matches, send, msgtype, nick):
        """ Handles scores

        | If it's a ++ add one point unless the user is trying to promote
        | themselves.
        | Otherwise substract one point.
        """
        scorefile = self.srcdir + '/data/score'
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
            json.dump(scores, f, indent=True, sort_keys=True)
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
            title = html.getroot().find(".//title").text.strip()
            # strip unicode
            title = title.encode('utf-8', 'ignore').decode().replace('\n', ' ')
        except URLError as ex:
            # website does not exist
            if hasattr(ex.reason, 'errno'):
                if ex.reason.errno == socket.EAI_NONAME or ex.reason.errno == errno.ENETUNREACH:
                    return
            else:
                send('%s: %s' % (type(ex).__name__, str(ex).replace('\n', ' ')))
                return
        # page does not contain a title
        except AttributeError:
            title = 'No Title Found'
        send('** %s - %s' % (title, shorturl))

    def do_mode(self, target, msg, nick, send):
        """ reop"""
        # reop
        botnick = self.config['core']['nick']
        match = re.search(r".*(-o|\+b).*%s" % botnick, msg)
        if match:
            self.connection.privmsg(target, "WAI U DO THIS " + nick + "?!??!")
            self.connection.privmsg("ChanServ", "OP " + target)
            self.connection.privmsg("ChanServ", "UNBAN " + target)

        # if user is guarded and quieted, devoiced, or deopped, fix that
        match = re.search(r"(.*(-v|-o|\+q|\+b)[^ ]*) (%s)" % "|".
                          join(self.guarded), msg)
        if match:
            self.connection.mode(target, " +voe-qb %s" % (match.group(3) * 5))

    def do_kick(self, c, send, target, nick, msg):
        """ Kick users.

        | If kick is disabled, don't do anything.
        | If the bot is not a op, rage at a op.
        | Kick the user.
        """
        if not self.kick_enabled:
            return
        if target not in self.channels:
            send("%s: you're lucky, private message kicking hasn't been implemented yet." % nick)
            return
        ops = list(self.channels[target].opers())
        if not ops:
            ops = ['someone']
        if nick not in ops:
            if self.config['core']['nick'] not in ops:
                c.privmsg(target, self.modules['creffett'].
                          gen_creffett("%s: /op the bot" % choice(ops)))
            elif random() < 0.01 and msg == "shutting caps lock off":
                c.kick(target, nick, "HUEHUEHUE GIBE CAPSLOCK PLS I REPORT U")
            else:
                c.kick(target, nick, self.modules['slogan'].
                       gen_slogan(msg).upper())

    def do_caps(self, msg, c, target, nick, send):
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
                self.do_kick(c, send, target, nick, text)
                self.caps.remove(nick)
            else:
                self.caps.append(nick)
        elif nick in self.caps:
            self.caps.remove(nick)

    def do_admin(self, c, cmd, cmdargs, send, nick, msgtype, target):
        if cmd == 'abuse':
            if cmdargs == 'clear':
                self.abuselist = {}
                send("Abuse list cleared.")
            elif cmdargs == 'show':
                send(str(self.abuselist))
        elif cmd == 'cadmin':
            admins = self.config['auth']['admins'].split(', ')
            self.admins = {nick: False for nick in admins}
            self.get_admins(c)
            send("Verified admins reset.")
        elif cmd == 'ignore':
            cmdargs = cmdargs.split()
            if cmdargs[0] == 'clear':
                self.ignored = []
                send("Ignore list cleared.")
            elif cmdargs[0] == 'show':
                if self.ignored:
                    send(", ".join(self.ignored))
                else:
                    send("Nobody is ignored.")
            elif cmdargs[0] == 'delete':
                if len(cmdargs) == 1:
                    send("Unignore who?")
                elif cmdargs[1] not in self.ignored:
                    send("%s is not ignored." % cmdargs[1])
                else:
                    self.ignored.remove(cmdargs[1])
                    send("%s is no longer ignored." % cmdargs[1])
            elif cmdargs[0] in self.ignored:
                send("%s is already ignored." % cmdargs[0])
            else:
                self.ignore(send, cmdargs[0])
        elif cmd == 'join':
            self.do_join(cmdargs, nick, msgtype, send, c)
        elif cmd == 'part':
            self.do_part(cmdargs, nick, target, msgtype, send, c)

    def do_band(self, msg, send):
        if ':' in msg:
            msg = msg.split(':')[1]
        if len(msg.split()) == 3 and random() < 0.005:
            send('"%s" would be a good name for a band...' % msg.strip())

    def do_args(self, modargs, send, nick, target, source, c):
        """ Handle the various args that modules need."""
        realargs = {}
        args = {'nick': nick,
                'channels': self.channels,
                'connection': self.connection,
                'modules': self.modules,
                'srcdir': self.srcdir,
                'logs': self.logs,
                'admins': self.admins,
                'issues': self.issues,
                'abuse': self.abuselist,
                'kick_enabled': self.kick_enabled,
                'guarded': self.guarded,
                'config': self.config,
                'source': source,
                'target': target if target[0] == "#" else "private",
                'do_kick': lambda target, nick, msg: self.do_kick(c, send, target, nick, msg),
                'is_admin': lambda nick: self.is_admin(c, nick),
                'ignore': lambda nick: self.ignore(send, nick)}
        for arg in modargs:
            if arg in args:
                realargs[arg] = args[arg]
            else:
                raise Exception("Invalid Argument: " + arg)
        return realargs

    def handle_msg(self, msgtype, c, e):
        """The Heart and Soul of IrcBot."""
        if msgtype == 'action':
            nick = e.source.split('!')[0]
        else:
            nick = e.source.nick
        if msgtype == 'mode':
            msg = " ".join(e.arguments)
        else:
            msg = e.arguments[0].strip()
        if msgtype == 'pub' or msgtype == 'action' or msgtype == 'mode':
            target = e.target
        else:
            target = nick
        send = lambda msg, mtype='privmsg': self.send(target, self.config['core']['nick'], msg, mtype)

        if msgtype == 'privnotice':
            self.set_admin(c, msg, send, nick, target)
            return
        # must come after set_admin to prevent spam
        self.do_log(target, nick, msg, msgtype)

        if msgtype == 'mode':
            self.do_mode(target, msg, nick, send)
            return

        if e.target == self.config['core']['ctrlchan']:
            control.handle_ctrlchan(self, msg, c, send)

        # crazy regex to match urls
        match = re.search(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.]
                              [a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()
                              <>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*
                              \)|[^\s`!()\[\]{};:'\".,<>?«»....]))""", msg)
        if match:
            self.do_urls(match, send)

        if not self.is_admin(c, nick, False) and nick in self.ignored:
            return

        cmdchar = self.config['core']['cmdchar']
        botnick = '%s: ' % self.config['core']['nick']
        if msg.startswith(botnick):
            msg = msg.replace(botnick, self.config['core']['cmdchar'])

        cmd = msg.split()[0]
        admins = self.config['auth']['admins'].split(', ')

        self.do_caps(msg, c, target, nick, send)
        if cmd[0] != cmdchar:
            self.do_band(msg, send)

        if cmd[1:] in self.disabled_mods:
            send("That module is disabled, sorry.")
            return

        # handle !s/a/b/
        if cmd[:2] == cmdchar + 's':
            cmd = cmd.split('/')[0]
        cmdargs = msg[len(cmd) + 1:]
        found = False
        if cmd[0] == cmdchar:
            if cmd[1:] in self.modules:
                mod = self.modules[cmd[1:]]
                if hasattr(mod, 'limit') and self.abusecheck(send, nick, mod.limit, msgtype, cmd[1:]):
                    return
                args = self.do_args(mod.args, send, nick, target, e.source, c) if hasattr(mod, 'args') else {}
                mod.cmd(send, cmdargs, args)
                found = True
        # special commands
        if cmd[0] == cmdchar:
            if cmd[1:] == 'reload':
                if nick not in admins:
                    send("Nope, not gonna do it.")
                else:
                    found = True
                    for x in self.modules.values():
                        imp.reload(x)
                    send("Aye Aye Capt'n")
                    self.get_admins(c)
            # everything below this point requires admin
            if not found and self.is_admin(c, nick):
                self.do_admin(c, cmd[1:], cmdargs, send, nick, msgtype, target)
        # ++ and --
        matches = re.findall(r"([a-zA-Z0-9]+)(\+\+|--)", msg)
        if matches:
            self.do_scores(matches, send, msgtype, nick)
