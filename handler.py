# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi,
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
import time
import sys
from helpers import control, sql, hook, command, textutils, admin, identity, misc
from os.path import dirname
from random import choice, random


class BotHandler():

    def __init__(self, config):
        """ Set everything up.

        | kick_enabled controls whether the bot will kick people or not.
        | caps is a array of the nicks who have abused capslock.
        | ignored is a array of the nicks who are currently ignored for
        |   bot abuse.
        | abuselist is a dict keeping track of how many times nicks have used
        |   rate-limited commands.
        | modules is a dict containing the commands the bot supports.
        | srcdir is the path to the directory where the bot is stored.
        | db - Is a db wrapper for data storage.
        """
        self.config = config
        start = time.time()
        self.uptime = {'start': start, 'reloaded': start}
        self.guarded = []
        self.outputfilter = [lambda x: x]
        self.kick_enabled = True
        self.caps = []
        self.ignored = []
        self.abuselist = {}
        admins = [x.strip() for x in config['auth']['admins'].split(',')]
        self.admins = {nick: -1 for nick in admins}
        self.loadmodules()
        self.hooks = self.loadhooks()
        self.srcdir = dirname(__file__)
        self.log_to_ctrlchan = False
        self.db = sql.Sql(config)

    def get_data(self):
        """Saves the handler's data for :func:`bot.do_reload`"""
        data = {}
        data['caps'] = list(self.caps)
        data['ignored'] = list(self.ignored)
        data['admins'] = dict(self.admins)
        data['uptime'] = dict(self.uptime)
        data['abuselist'] = dict(self.abuselist)
        data['guarded'] = list(self.guarded)
        return data

    def set_data(self, data):
        """Called from :func:`bot.do_reload` to restore the handler's data."""
        for key, val in data.items():
            setattr(self, key, val)
        return

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
        if nick not in [x.strip() for x in self.config['auth']['admins'].split(',')]:
            return False
        # unauthed
        if nick not in self.admins:
            self.admins[nick] = -1
        if self.admins[nick] == -1:
            self.connection.privmsg('NickServ', 'ACC %s' % nick)
            if complain:
                send("Unverified admin: %s" % nick, target=self.config['core']['channel'])
            return False
        else:
            # reverify every 5min
            if int(time.time()) - self.admins[nick] > 300:
                self.connection.privmsg('NickServ', 'ACC %s' % nick)
            return True

    def get_admins(self, c):
        """Check verification for all admins."""
        for a in self.admins:
            c.privmsg('NickServ', 'ACC %s' % a)

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
            self.do_kick(send, target, nick, msg, False)
            return True

    def send(self, target, nick, msg, msgtype):
        """ Send a message.

        Records the message in the log.
        """
        msgs = []
        for i in self.outputfilter:
            msg = i(msg)
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

        | Logs to a sql db.
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
        if not cmdargs:
            send("Join what?")
            return
        if cmdargs == '0':
            send("I'm sorry, Dave. I'm afraid I can't do that.")
            return
        if cmdargs[0] != '#':
            cmdargs = '#' + cmdargs
        cmd = cmdargs.split()
        if cmd[0] in self.channels and not (len(cmd) > 1 and cmd[1] == "force"):
            send("%s is already a member of %s" % (self.config['core']['nick'],
                 cmd[0]))
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

    def do_kick(self, send, target, nick, msg, slogan=True):
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
        botnick = self.config['core']['nick']
        if not ops:
            ops = ['someone']
        if nick not in ops:
            if botnick not in ops and botnick != 'someone':
                send(textutils.gen_creffett("%s: /op the bot" % choice(ops)), target=target)
            elif random() < 0.01 and msg == "shutting caps lock off":
                self.connection.kick(target, nick, "HUEHUEHUE GIBE CAPSLOCK PLS I REPORT U")
            else:
                msg = textutils.gen_slogan(msg).upper() if slogan else msg
                self.connection.kick(target, nick, msg)

    def do_admin(self, c, cmd, cmdargs, send, nick, msgtype, target):
        if cmd == 'abuse':
            if cmdargs == 'clear':
                self.abuselist = {}
                send("Abuse list cleared.")
            elif cmdargs == 'show':
                abusers = [x for x in self.abuselist.keys() if x in self.ignored]
                send(", ".join(abusers))
        elif cmd == 'cadmin':
            admins = [x.strip() for x in self.config['auth']['admins'].split(',')]
            self.admins = {nick: False for nick in admins}
            self.get_admins(c)
            send("Verified admins reset.")
        elif cmd == 'ignore':
            cmdargs = cmdargs.split()
            if not cmdargs:
                send("Ignore who?")
            elif cmdargs[0] == 'clear':
                self.ignored = []
                send("Ignore list cleared.")
            elif cmdargs[0] == 'show' or cmdargs[0] == 'list':
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
        elif cmd == 'quit':
            c.disconnect('Goodbye, Cruel World!')
            sys.exit(0)

    def do_args(self, modargs, send, nick, target, source, c, name, msgtype):
        """ Handle the various args that modules need."""
        realargs = {}
        args = {'nick': nick,
                'handler': self,
                'db': self.db.get(),
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

    def do_reload(self):
        self.uptime['reloaded'] = time.time()
        self.loadmodules()
        self.loadhooks()

    def handle_msg(self, msgtype, c, e):
        """The Heart and Soul of IrcBot."""

        # actions don't have the nick attr for some reason
        if msgtype == 'action':
            nick = e.source.split('!')[0]
        else:
            nick = e.source.nick

        # modes have separate arguments, everything else just one
        if msgtype == 'mode' or msgtype == 'nick' or msgtype == 'join':
            msg = " ".join(e.arguments)
        else:
            msg = e.arguments[0].strip()

        # Send the response to private messages to the sending nick.
        if msgtype == 'privmsg' or msgtype == 'privnotice':
            target = nick
        else:
            target = e.target

        send = lambda msg, mtype='privmsg', target=target: self.send(target, self.config['core']['nick'], msg, mtype)

        if msgtype == 'privnotice':
            if not hasattr(self, 'connection'):
                return
            if nick == 'NickServ':
                admin.set_admin(msg, self)
                return

        if self.config['feature'].getboolean('hooks') and nick not in self.ignored:
            for hook in self.hooks:
                realargs = self.do_args(hook.args, send, nick, target, e.source, c, hook, msgtype)
                hook.run(send, msg, msgtype, self, target, realargs)

        if msgtype == 'nick':
            if e.target in self.admins:
                c.privmsg('NickServ', 'ACC %s' % e.target)
            if identity.handle_nick(self, e):
                for x in misc.get_channels(self.channels, e.target):
                    self.do_kick(send, x, e.target, "identity crisis")
            return

        # must come after set_admin to prevent spam
        self.do_log(target, nick, msg, msgtype)

        if msgtype == 'mode':
            self.do_mode(target, msg, nick, send)
            return

        if msgtype == 'join':
            if nick == c.real_nickname:
                send("Joined channel %s" % target, target=self.config['core']['ctrlchan'])
            return

        # ignore empty messages
        if not msg:
            return

        if e.target == self.config['core']['ctrlchan']:
            control.handle_ctrlchan(self, msg, c, send)

        if not self.is_admin(send, nick, False) and nick in self.ignored:
            return

        msg = misc.get_cmdchar(self.config, c, msg, msgtype)
        cmd = msg.split()[0]
        cmdchar = self.config['core']['cmdchar']
        admins = [x.strip() for x in self.config['auth']['admins'].split(',')]
        
        if msgtype == "pubnotice":
            return
        
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
                # Duplicate command
                if command.check_command(self.db.get(), nick, msg, target):
                    return
                args = self.do_args(cmd_obj.args, send, nick, target, e.source, c, cmd_name, msgtype)
                cmd_obj.run(send, cmdargs, args, cmd_name, nick, target, self)
        # special commands
        if cmd.startswith(cmdchar):
            if cmd[len(cmdchar):] == 'reload':
                if nick in admins:
                    found = True
                    self.do_reload()
                    send("Aye Aye Capt'n")
            # everything below this point requires admin
            if not found and self.is_admin(send, nick):
                self.do_admin(c, cmd[len(cmdchar):], cmdargs, send, nick, msgtype, target)
