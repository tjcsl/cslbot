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
import imp
import time
import sys
from helpers import control, sql, hook, command, textutils
from os.path import dirname
from random import choice, random


class BotHandler():

    def __init__(self, config):
        """ Set everything up.

        | kick_enabled controls whether the bot will kick people or not.
        | caps is a array of the nicks who have abused capslock.
        | ignored is a array of the nicks who are currently ignored for
        |   bot abuse.
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
        self.outputfilter = lambda x: x
        self.kick_enabled = True
        self.caps = []
        self.ignored = []
        self.issues = []
        self.channels = {}
        self.abuselist = {}
        admins = config['auth']['admins'].split(', ')
        self.admins = {nick: None for nick in admins}
        self.loadmodules()
        self.hooks = self.loadhooks()
        self.srcdir = dirname(__file__)
        self.log_to_ctrlchan = False
        self.db = sql.Sql()

    def get_data(self):
        """Saves the handler's data for :func:`bot.do_reload`"""
        data = {}
        data['caps'] = list(self.caps)
        data['ignored'] = list(self.ignored)
        data['issues'] = list(self.issues)
        data['channels'] = dict(self.channels)
        data['abuselist'] = dict(self.abuselist)
        data['guarded'] = list(self.guarded)
        return data

    def set_data(self, data):
        """Called from :func:`bot.do_reload` to restore the handler's data."""
        self.caps = data['caps']
        self.ignored = data['ignored']
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
        command.scan_for_commands(dirname(__file__) + '/commands')

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

    def is_admin(self, send, nick, complain=True):
        """Checks if a nick is a admin.

        | If the nick is not in :const:`ADMINS` then it's not a admin.
        | If NickServ hasn't responded yet, then the admin is unverified,
        | so assume they aren't a admin.
        """
        if nick not in self.config['auth']['admins'].split(', '):
            return False
        send('ACC %s' % nick, target='NickServ')
        if not self.admins[nick] and self.admins[nick] is not None:
            if complain:
                send("Unverified admin: %s" % nick, target=self.config['core']['channel'])
            return False
        else:
            return True

    def get_admins(self, c):
        """Check verification for all admins."""
        for admin in self.admins:
            c.privmsg('NickServ', 'ACC %s' % admin)

    def abusecheck(self, send, nick, target, limit, cmd):
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
            text = "%s: don't abuse scores" if cmd == 'scores' else "%s: stop abusing the bot"
            msg = textutils.gen_creffett(text % nick)
            send(msg, target=target)
            self.ignore(send, nick)
            return True

    def send(self, target, nick, msg, msgtype):
        """ Send a message.

        Records the message in the log.
        """
        msgs = []
        msg = self.outputfilter(msg)
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
        # We don't log NickServ auth calls.
        if msgtype == 'privnotice':
            return
        if not isinstance(msg, str):
            raise Exception("IRC doesn't like it when you send it a %s" % type(msg).__name__)
        target = target.lower()
        flags = 0
        if target[0] == "#":
            if target in self.channels and nick in self.channels[target].opers():
                    flags |= 1
            if target in self.channels and nick in self.channels[target].voiced():
                    flags |= 2
        else:
            target = 'private'
        # strip ctrl chars from !creffett
        msg = msg.replace('\x02\x038,4', '<rage>')
        # strip non-printable chars
        msg = ''.join(c for c in msg if ord(c) > 31 and ord(c) < 127)
        self.db.log(nick, target, flags, msg, msgtype)

        if self.log_to_ctrlchan:
            ctrlchan = self.config['core']['ctrlchan']
            if target != ctrlchan:
                ctrlmsg = "%s:%s:%s:%s" % (target, msgtype, nick, msg)
                # If we call self.send, we'll get a infinite loop.
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

    def do_mode(self, target, msg, nick, send):
        """ reop"""
        # reop
        botnick = self.config['core']['nick']
        match = re.search(r".*(-o|\+b).*%s" % botnick, msg)
        if match:
            send("%s: :(" % nick, target=target)
            send("OP %s" % target, target='ChanServ')
            send("UNBAN %s" % target, target='ChanServ')

        # if user is guarded and quieted, devoiced, or deopped, fix that
        match = re.search(r"(.*(-v|-o|\+q|\+b)[^ ]*) (%s)" % "|".
                          join(self.guarded), msg)
        if match:
            self.connection.mode(target, " +voe-qb %s" % (match.group(3) * 5))

    def do_kick(self, send, target, nick, msg):
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
                send(textutils.gen_creffett("%s: /op the bot" % choice(ops)), target=target)
            elif random() < 0.01 and msg == "shutting caps lock off":
                self.connection.kick(target, nick, "HUEHUEHUE GIBE CAPSLOCK PLS I REPORT U")
            else:
                self.connection.kick(target, nick, textutils.gen_slogan(msg).upper())

    def do_admin(self, c, cmd, cmdargs, send, nick, msgtype, target):
        if cmd == 'abuse':
            if cmdargs == 'clear':
                self.abuselist = {}
                send("Abuse list cleared.")
            elif cmdargs == 'show':
                send(",".join(self.abuselist.keys()))
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

    def do_args(self, modargs, send, nick, target, source, c, name, msgtype):
        """ Handle the various args that modules need."""
        realargs = {}
        args = {'nick': nick,
                'channels': self.channels,
                'connection': self.connection,
                'srcdir': self.srcdir,
                'admins': self.admins,
                'issues': self.issues,
                'abuselist': self.abuselist,
                'handler': self,
                'db': self.db.get(),
                'kick_enabled': self.kick_enabled,
                'guarded': self.guarded,
                'config': self.config,
                'source': source,
                'name': name,
                'type': msgtype,
                'botnick': self.connection.real_nickname,
                'target': target if target[0] == "#" else "private",
                'do_kick': lambda target, nick, msg: self.do_kick(send, target, nick, msg),
                'is_admin': lambda nick: self.is_admin(send, nick),
                'ignore': lambda nick: self.ignore(send, nick),
                'abuse': lambda nick, limit, cmd: self.abusecheck(send, nick, target, limit, cmd)}
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
        if msgtype == 'pubmsg' or msgtype == 'pubnotice' or msgtype == 'action' or msgtype == 'mode':
            target = e.target
        else:
            target = nick
        send = lambda msg, mtype='privmsg', target=target: self.send(target, self.config['core']['nick'], msg, mtype)

        for hook in self.hooks:
            realargs = self.do_args(hook.args, send, nick, target, e.source, c, hook, msgtype)
            hook.run(send, msg, msgtype, realargs)

        # must come after set_admin to prevent spam
        self.do_log(target, nick, msg, msgtype)

        if msgtype == 'mode':
            self.do_mode(target, msg, nick, send)
            return

        if e.target == self.config['core']['ctrlchan']:
            control.handle_ctrlchan(self, msg, c, send)

        if not self.is_admin(send, nick, False) and nick in self.ignored:
            return

        cmdchar = self.config['core']['cmdchar']
        botnick = '%s: ' % self.connection.real_nickname
        if msg.startswith(botnick):
            msg = msg.replace(botnick, self.config['core']['cmdchar'])

        cmd = msg.split()[0]
        admins = self.config['auth']['admins'].split(', ')

        # handle !s
        cmdlen = len(cmd) + 1
        if cmd.startswith('%ss' % cmdchar):
            match = re.match('%ss(\W)' % cmdchar, cmd)
            if match:
                cmd = cmd.split(match.group(1))[0]
                cmdlen = len(cmd)
        cmdargs = msg[cmdlen:]
        found = False
        if cmd.startswith(cmdchar):
            cmd_name = cmd[len(cmdchar):]
            if command.is_registered(cmd_name):
                found = True
                cmd_obj = command.get_command(cmd_name)
                if cmd_obj.is_limited() and self.abusecheck(send, nick, target, cmd_obj.limit, cmd[len(cmdchar):]):
                    return
                args = self.do_args(cmd_obj.args, send, nick, target, e.source, c, cmd_name, msgtype)
                cmd_obj.run(send, cmdargs, args, cmd_name, nick, target, self.db.get())
        # special commands
        if cmd.startswith(cmdchar):
            if cmd[len(cmdchar):] == 'reload':
                if nick not in admins:
                    send("Nope, not gonna do it.")
                else:
                    found = True
                    self.clean_sql_connection_pool()
                    imp.reload(sys.modules['helpers.command'])
                    imp.reload(sys.modules['helpers.control'])
                    imp.reload(sys.modules['helpers.hook'])
                    imp.reload(sys.modules['helpers.sql'])
                    imp.reload(sys.modules['helpers.textutils'])
                    imp.reload(sys.modules['helpers.urlutils'])
                    self.loadmodules()
                    self.loadhooks()
                    send("Aye Aye Capt'n")
                    self.get_admins(c)
            # everything below this point requires admin
            if not found and self.is_admin(send, nick):
                self.do_admin(c, cmd[len(cmdchar):], cmdargs, send, nick, msgtype, target)
