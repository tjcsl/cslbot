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
import importlib
import imp
import time
import socket
import string
import sys
import errno
from helpers import control, sql, hook
from os.path import basename, dirname
from glob import glob
from lxml.html import parse
from urllib.request import urlopen, Request
from urllib.error import URLError
from random import choice, random


class BotHandler():

    def __init__(self, config):
        """ Set everything up.

        | kick_enabled controls whether the bot will kick people or not.
        | caps is a array of the nicks who have abused capslock.
        | ignored is a array of the nicks who are currently ignored for
        |   bot abuse.
        | disabled_mods is a array of the currently disabled modules.
        | issues is a list keeping track of pending issues.
        | channels is a dict containing the objects for each channel the bot
        |   is connected to.
        | abuselist is a dict keeping track of how many times nicks have used
        |   rate-limited commands.
        | modules is a dict containing the commands the bot supports.
        | srcdir is the path to the directory where the bot is stored.
        | db - Is a db wrapper for data storage.
        """
        self.config = config
        self.guarded = []
        self.kick_enabled = True
        self.caps = []
        self.ignored = []
        self.disabled_mods = []
        self.issues = []
        self.channels = {}
        self.abuselist = {}
        admins = config['auth']['admins'].split(', ')
        self.admins = {nick: None for nick in admins}
        self.modules = self.loadmodules()
        self.hooks = self.loadhooks()
        self.srcdir = dirname(__file__)
        self.log_to_ctrlchan = False
        self.db = sql.Sql()

    def get_data(self):
        """Saves the handler's data for :func:`bot.do_reload`"""
        data = {}
        data['caps'] = list(self.caps)
        data['ignored'] = list(self.ignored)
        data['disabled_mods'] = list(self.disabled_mods)
        data['issues'] = list(self.issues)
        data['channels'] = dict(self.channels)
        data['abuselist'] = dict(self.abuselist)
        data['guarded'] = list(self.guarded)
        return data

    def set_data(self, data):
        """Called from :func:`bot.do_reload` to restore the handler's data."""
        self.caps = data['caps']
        self.ignored = data['ignored']
        self.disabled_mods = data['disabled_mods']
        self.issues = data['issues']
        self.channels = data['channels']
        self.abuselist = data['abuselist']
        self.guarded = data['guarded']

    def clean_sql_connection_pool(self):
        """ Cleans the sql connection pool."""
        self.db.clean_connection_pool()

    @staticmethod
    def loadmodules():
        """Load all the commands.

        | Globs over all the .py files in the commands dir.
        | Skips file without the executable bit set
        | Imports the modules into a dict
        """
        modulemap = {}
        for f in glob(dirname(__file__) + '/commands/*.py'):
            if os.access(f, os.X_OK):
                cmd = basename(f).split('.')[0]
                modulemap[cmd] = importlib.import_module("commands." + cmd)
        return modulemap

    @staticmethod
    def loadhooks():
        """Load all the hooks.

        | Globs over all the .py files in the hooks dir.
        | Skips file without the executable bit set
        | Imports the hooks into a dict
        """
        return hook.scan_for_hooks(dirname(__file__) + '/hooks')

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
        if not self.admins[nick] and self.admins[nick] is not None:
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
        elif msg.startswith('%sgcc' % cmdchar):
            self.send(nick, nick, 'GCC is a group excercise!', e.type)
        elif msg.startswith('%svote' % cmdchar) or msg.startswith('%spoll' % cmdchar):
            self.send(nick, nick, "We don't have secret ballots in this benevolent dictatorship!", e.type)
        elif re.search(r"(%s+)(\+\+|--)" % self.config['core']['nickregex'], msg):
            self.send(nick, nick, 'Hey, no points in private messages!', e.type)
        else:
            self.handle_msg('privmsg', c, e)

    def pubmsg(self, c, e):
        """ Handle public messages.

        Forward messages to :func:`handle_msg`.
        """
        self.handle_msg('pubmsg', c, e)

    def privnotice(self, c, e):
        """ Handle private notices.

        Forward notices to :func:`handle_msg`.
        """
        self.handle_msg('privnotice', c, e)

    def pubnotice(self, c, e):
        """ Handle public notices.

        Forward notices to :func:`handle_msg`.
        """
        self.handle_msg('pubnotice', c, e)

    def action(self, c, e):
        """ Handle actions.

        Forward actions to :func:`handle_msg`.
        """
        self.handle_msg('action', c, e)

    def mode(self, c, e):
        """ Handle actions.

        Forward mode changes to :func:`handle_msg`.
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

        | Logs to a sqlite db.
        """
        if not isinstance(msg, str):
            raise Exception("IRC doesn't like it when you send it a " +
                            type(msg).__name__)
        target = target.lower()
        isop = False
        if target[0] == "#":
            if target in self.channels and nick in self.channels[target].opers():
                    isop = True
        else:
            target = 'private'
        # strip ctrl chars from !creffett
        msg = msg.replace('\x02\x038,4', '<rage>')
        # strip non-printable chars
        msg = ''.join(c for c in msg if ord(c) > 31 and ord(c) < 127)
        self.db.log(nick, target, isop, msg, msgtype)

        if self.log_to_ctrlchan:
            ctrlchan = self.config['core']['ctrlchan']
            if target != ctrlchan:
                ctrlmsg = "%s:%s:%s:%s" % (target, msgtype, nick, msg)
                self.connection.privmsg(ctrlchan, ctrlmsg.strip())

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
        self.send(cmd[0], nick, "Joined at the request of " + nick, msgtype)

    def do_scores(self, matches, send, msgtype, nick):
        """ Handles scores

        | If it's a ++ add one point unless the user is trying to promote
        | themselves.
        | Otherwise substract one point.
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
            #TODO: maybe we can do this with INSERT OR REPLACE?
            cursor = self.db.get()
            if cursor.execute("SELECT count(1) FROM scores WHERE nick=?", (name,)).fetchone()[0] == 1:
                cursor.execute("UPDATE scores SET score=score+? WHERE nick=?", (score, name))
            else:
                cursor.execute("INSERT INTO scores(score,nick) VALUES(?,?)", (score, name))

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

    def do_args(self, modargs, send, nick, target, source, c):
        """ Handle the various args that modules need."""
        realargs = {}
        args = {'nick': nick,
                'channels': self.channels,
                'connection': self.connection,
                'modules': self.modules,
                'srcdir': self.srcdir,
                'admins': self.admins,
                'issues': self.issues,
                'abuse': self.abuselist,
                'db': self.db.get(),
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

    def do_stallman(self, msg, nick, send):
        msgl = msg.lower()
        if "linux" in msgl and "gnu/linux" not in msgl and self.config['feature']['stallmanmode'] == "True":
            send(nick + ": I'd just like to interject for a moment. What you're referring to as Linux, is in fact, GNU/Linux, or as I've recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.")
            send("Many computer users run a modified version of the GNU system every day, without realizing it. Through a peculiar turn of events, the version of GNU which is widely used today is often called 'Linux', and many of its users are not aware that it is basically the GNU system, developed by the GNU Project. There really is a Linux, and these people are using it, but it is just a part of the system they use.")
            send("Linux is the kernel: the program in the system that allocates the machine's resources to the other programs that you run. The kernel is an essential part of an operating system, but useless by itself; it can only function in the context of a complete operating system. Linux is normally used in combination with the GNU operating system: the whole system is basically GNU with Linux added, or GNU/Linux. All the so-called 'Linux' distributions are really distributions of GNU/Linux.")

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
        if msgtype == 'pubmsg' or msgtype == 'pubnotice' or msgtype == 'action' or msgtype == 'mode':
            target = e.target
        else:
            target = nick
        send = lambda msg, mtype='privmsg': self.send(target, self.config['core']['nick'], msg, mtype)

        for hook in self.hooks:
            realargs = self.do_args(hook.reqargs, send, nick, target, e.source, c)
            hook.run(send, msg, msgtype, realargs)

        if msgtype == 'privnotice':
            self.set_admin(c, msg, send, nick, target)
            return

        # must come after set_admin to prevent spam
        self.do_log(target, nick, msg, msgtype)

        if msgtype == 'mode':
            self.do_mode(target, msg, nick, send)
            return

        # Stallman mode
        self.do_stallman(msg, nick, send)

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
        botnick = '%s: ' % self.connection.real_nickname
        if msg.startswith(botnick):
            msg = msg.replace(botnick, self.config['core']['cmdchar'])

        cmd = msg.split()[0]
        admins = self.config['auth']['admins'].split(', ')

        self.do_caps(msg, c, target, nick, send)

        if cmd[len(cmdchar):] in self.disabled_mods:
            send("That module is disabled, sorry.")
            return

        # handle !s/a/b/
        if cmd.startswith('%ss/' % cmdchar):
            cmd = cmd.split('/')[0]
        cmdargs = msg[len(cmd) + 1:]
        found = False
        if cmd.startswith(cmdchar):
            if cmd[len(cmdchar):] in self.modules:
                mod = self.modules[cmd[len(cmdchar):]]
                if hasattr(mod, 'limit') and self.abusecheck(send, nick, mod.limit, msgtype, cmd[len(cmdchar):]):
                    return
                args = self.do_args(mod.args, send, nick, target, e.source, c) if hasattr(mod, 'args') else {}
                mod.cmd(send, cmdargs, args)
                found = True
        # special commands
        if cmd.startswith(cmdchar):
            if cmd[len(cmdchar):] == 'reload':
                if nick not in admins:
                    send("Nope, not gonna do it.")
                else:
                    found = True
                    self.clean_sql_connection_pool()
                    for x in self.modules.values():
                        imp.reload(x)
                    #reload hooks
                    imp.reload(sys.modules['modules.hook'])
                    self.loadhooks()
                    send("Aye Aye Capt'n")
                    self.get_admins(c)
            # everything below this point requires admin
            if not found and self.is_admin(c, nick):
                self.do_admin(c, cmd[len(cmdchar):], cmdargs, send, nick, msgtype, target)
        # ++ and --
        matches = re.findall(r"(%s+)(\+\+|--)" % self.config['core']['nickregex'], msg)
        if matches:
            self.do_scores(matches, send, msgtype, nick)
