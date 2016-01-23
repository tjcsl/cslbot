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

import base64
import collections
import copy
import functools
import logging
import random
import re
import threading
import time
from datetime import datetime, timedelta

from irc import modes

from . import (admin, arguments, command, control, hook, identity, misc, orm,
               sql, textutils, tokens, workers)


class BotHandler():

    def __init__(self, config, connection, channels, confdir):
        """ Set everything up.

        | kick_enabled controls whether the bot will kick people or not.
        | caps is a array of the nicks who have abused capslock.
        | abuselist is a dict keeping track of how many times nicks have used
        |   rate-limited commands.
        | modules is a dict containing the commands the bot supports.
        | confdir is the path to the directory where the bot's config is stored.
        | db - Is a db wrapper for data storage.
        """
        self.connection = connection
        self.channels = channels
        self.config = config
        self.db = sql.Sql(config, confdir)
        self.workers = workers.Workers(self)
        self.caps = []
        self.guarded = []
        self.admins = {nick.strip(): None for nick in config['auth']['admins'].split(',')}
        self.voiced = collections.defaultdict(dict)
        self.opers = collections.defaultdict(dict)
        self.features = {'account-notify': False, 'extended-join': False, 'whox': False}
        start = datetime.now()
        self.uptime = {'start': start, 'reloaded': start}
        self.abuselist = {}
        self.ping_map = {}
        self.outputfilter = collections.defaultdict(list)
        self.kick_enabled = True
        self.who_map = {}
        self.flood_lock = threading.Lock()
        self.data_lock = threading.RLock()
        self.last_msg_time = datetime.now()
        self.confdir = confdir
        self.log_to_ctrlchan = False

    def get_data(self):
        """Saves the handler's data for :func:`bot.IrcBot.do_reload`"""
        data = {}
        data['caps'] = self.caps[:]
        data['guarded'] = self.guarded[:]
        data['admins'] = self.admins.copy()
        data['voiced'] = copy.deepcopy(self.voiced)
        data['opers'] = copy.deepcopy(self.opers)
        data['features'] = self.features.copy()
        data['uptime'] = self.uptime.copy()
        data['abuselist'] = self.abuselist.copy()
        return data

    def set_data(self, data):
        """Called from :func:`bot.IrcBot.do_reload` to restore the handler's data."""
        for key, val in data.items():
            setattr(self, key, val)
        self.uptime['reloaded'] = datetime.now()

    def update_authstatus(self, nick):
        if self.features['whox']:
            tag = random.randint(0, 999)
            # This just maps it off into nothingness, but that's okay, we just care about the auth
            self.who_map[tag] = nick
            self.connection.who('%s %%naft,%d' % (nick, tag))
        elif self.config['feature']['servicestype'] == "ircservices":
            self.connection.privmsg('NickServ', 'STATUS %s' % nick)
        elif self.config['feature']['servicestype'] == "atheme":
            self.connection.privmsg('NickServ', 'ACC %s' % nick)

    def is_admin(self, send, nick):
        """Checks if a nick is a admin.

        | If the nick is not in self.admins then it's not a admin.
        | If NickServ hasn't responded yet, then the admin is unverified,
        | so assume they aren't a admin.
        """
        if nick not in [x.strip() for x in self.config['auth']['admins'].split(',')]:
            return False
        # no nickserv support, assume people are who they say they are.
        if not self.config['feature'].getboolean('nickserv'):
            return True
        # unauthed
        if nick not in self.admins:
            self.admins[nick] = None
        if self.admins[nick] is None:
            self.update_authstatus(nick)
            # We don't necessarily want to complain in all cases.
            if send is not None:
                send("Unverified admin: %s" % nick, target=self.config['core']['channel'])
            return False
        else:
            if not self.features['account-notify']:
                # reverify every 5min
                if datetime.now() - self.admins[nick] > timedelta(minutes=5):
                    self.update_authstatus(nick)
            return True

    def get_admins(self):
        """Check verification for all admins."""
        # no nickserv support, assume people are who they say they are.
        if not self.config['feature'].getboolean('nickserv'):
            return
        for i, a in enumerate(self.admins):
            if a is None:
                self.workers.defer(i, False, self.update_authstatus, a)

    def abusecheck(self, send, nick, target, limit, cmd):
        """ Rate-limits commands.

        | If a nick uses commands with the limit attr set, record the time
        | at which they were used.
        | If the command is used more than `limit` times in a
        | minute, ignore the nick.
        """
        if nick not in self.abuselist:
            self.abuselist[nick] = {}
        if cmd not in self.abuselist[nick]:
            self.abuselist[nick][cmd] = [datetime.now()]
        else:
            self.abuselist[nick][cmd].append(datetime.now())
        count = 0
        for x in self.abuselist[nick][cmd]:
            # 60 seconds - arbitrary cuttoff
            if datetime.now() - x < timedelta(seconds=60):
                count = count + 1
        if count > limit:
            msg = "%s: don't abuse scores!" if cmd == 'scores' else "%s: stop abusing the bot!"
            send(msg % nick, target=target)
            with self.db.session_scope() as session:
                send(misc.ignore(session, nick))
            return True

    @staticmethod
    def get_max_length(target, msgtype):
        overhead = r"PRIVMSG %s: \r\n" % target
        # FIXME: what the hell is up w/ message length limits?
        if msgtype == 'action':
            overhead += "\001ACTION \001"
            max_len = 454  # 512
        else:
            max_len = 453  # 512
        return max_len - len(overhead.encode())

    def send(self, target, nick, msg, msgtype, ignore_length=False, filters=None):
        """ Send a message.

        Records the message in the log.
        """
        if not isinstance(msg, str):
            raise Exception("Trying to send a %s to irc, only strings allowed." % type(msg).__name__)
        msgs = []
        if filters is None:
            filters = self.outputfilter[target]
        for i in filters:
            if target != self.config['core']['ctrlchan']:
                msg = i(msg)
        # Avoid spam from commands that produce excessive output.
        max_len = 650
        msg = [x.encode() for x in msg]
        if functools.reduce(lambda x, y: x + len(y), msg, 0) > max_len and not ignore_length:
            msg, _ = misc.split_msg(msg, max_len)
            msg += "..."
            msg = [x.encode() for x in msg]
        max_len = self.get_max_length(target, msgtype)
        # We can't send messages > 512 bytes to irc.
        while functools.reduce(lambda x, y: x + len(y), msg, 0) > max_len:
            split, msg = misc.split_msg(msg, max_len)
            msgs.append(split)
        msgs.append(''.join([x.decode() for x in msg]).strip())
        for i in msgs:
            self.do_log(target, nick, i, msgtype)
            if msgtype == 'action':
                self.rate_limited_send('action', target, i)
            else:
                self.rate_limited_send('privmsg', target, i)

    def rate_limited_send(self, mtype, target, msg):
        with self.flood_lock:
            elapsed = datetime.now() - self.last_msg_time
            # Don't send messages more then once every 0.5 sec.
            time.sleep(max(0, 0.5 - elapsed.total_seconds()))
            getattr(self.connection, mtype)(target, msg)
            self.last_msg_time = datetime.now()

    def do_log(self, target, nick, msg, msgtype):
        """ Handles logging.

        | Logs to a sql db.
        """
        if not isinstance(msg, str):
            raise Exception("IRC doesn't like it when you send it a %s" % type(msg).__name__)
        target = target.lower()
        flags = 0
        # Properly handle /msg +#channel
        if target.startswith(('+', '@')):
            target = target[1:]
        with self.data_lock:
            if target in self.channels:
                if nick in self.opers[target]:
                    flags |= 1
                if nick in self.voiced[target]:
                    flags |= 2
            else:
                target = 'private'
        # FIXME: should we special-case this?
        # strip ctrl chars from !creffett
        msg = msg.replace('\x02\x038,4', '<rage>')
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
        if not cmdargs.startswith(('#', '+', '@')):
            cmdargs = '#' + cmdargs
        # don't leave the primary channel
        if cmdargs == channel:
            send("%s must have a home." % botnick)
            return
        # don't leave the control channel
        if cmdargs == self.config['core']['ctrlchan']:
            send("%s must remain under control, or bad things will happen." % botnick)
            return
        self.send(cmdargs, nick, "Leaving at the request of %s" % nick, msgtype)
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
        if not cmdargs.startswith(('#', '+', '@')):
            cmdargs = '#' + cmdargs
        cmd = cmdargs.split()
        # FIXME: use argparse
        if cmd[0] in self.channels and not (len(cmd) > 1 and cmd[1] == "force"):
            send("%s is already a member of %s" % (self.config['core']['nick'],
                                                   cmd[0]))
            return
        c.join(cmd[0])
        self.send(cmd[0], nick, "Joined at the request of " + nick, msgtype)

    def check_mode(self, mode):
        if mode[2] != self.connection.real_nickname:
            return False
        if (mode[0], mode[1]) == ('-', 'o'):
            return True
        elif (mode[0], mode[1]) == ('+', 'b'):
            return True
        return False

    def do_mode(self, target, msg, nick, send):
        """ reop and handle guard violations """
        mode_changes = modes.parse_channel_modes(msg)
        with self.data_lock:
            for change in mode_changes:
                if change[1] == 'v':
                    self.voiced[target][change[2]] = True if change[0] == '+' else False
                if change[1] == 'o':
                    self.opers[target][change[2]] = True if change[0] == '+' else False
        # reop
        # FIXME: handle -o+o msbobBot msbobBot
        if [x for x in mode_changes if self.check_mode(x)]:
            send("%s: :(" % nick, target=target)
            # Assume bot admins know what they're doing.
            if not self.is_admin(None, nick):
                send("OP %s" % target, target='ChanServ')
                send("UNBAN %s" % target, target='ChanServ')

        if len(self.guarded) > 0:
            # if user is guarded and quieted, devoiced, or deopped, fix that
            regex = r"(.*(-v|-o|\+q|\+b)[^ ]*) (%s)" % "|".join(self.guarded)
            match = re.search(regex, msg)
            if match and nick not in [match.group(3), self.connection.real_nickname]:
                modestring = "+voe-qb %s" % (" ".join([match.group(3)] * 5))
                self.connection.mode(target, modestring)
                send('Mode %s on %s by the guard system' % (modestring, target), target=self.config['core']['ctrlchan'])

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
        with self.data_lock:
            ops = [k for k, v in self.opers[target].items() if v]
        botnick = self.config['core']['nick']
        if botnick not in ops:
            ops = ['someone'] if not ops else ops
            send(textutils.gen_creffett("%s: /op the bot" % random.choice(ops)), target=target)
        elif random.random() < 0.01 and msg == "shutting caps lock off":
            if nick in ops:
                send("%s: HUEHUEHUE GIBE CAPSLOCK PLS I REPORT U" % nick, target=target)
            else:
                self.connection.kick(target, nick, "HUEHUEHUE GIBE CAPSLOCK PLS I REPORT U")
        else:
            msg = textutils.gen_slogan(msg).upper() if slogan else msg
            if nick in ops:
                send("%s: %s" % (nick, msg), target=target)
            else:
                self.connection.kick(target, nick, msg)

    def do_args(self, modargs, send, nick, target, source, name, msgtype):
        """ Handle the various args that modules need."""
        realargs = {}
        args = {'nick': nick,
                'handler': self,
                'db': None,
                'config': self.config,
                'source': source,
                'name': name,
                'type': msgtype,
                'botnick': self.connection.real_nickname,
                'target': target if target[0] == "#" else "private",
                'do_kick': lambda target, nick, msg: self.do_kick(send, target, nick, msg),
                'is_admin': lambda nick: self.is_admin(send, nick),
                'abuse': lambda nick, limit, cmd: self.abusecheck(send, nick, target, limit, cmd)}
        for arg in modargs:
            if arg in args:
                realargs[arg] = args[arg]
            else:
                raise Exception("Invalid Argument: %s" % arg)
        return realargs

    def do_welcome(self):
        """Do setup when connected to server.

        | Join the primary channel.
        | Join the control channel.
        """
        tokens.update_all_tokens(self.config)
        self.connection.join(self.config['core']['channel'])
        self.connection.join(self.config['core']['ctrlchan'], self.config['auth']['ctrlkey'])
        # We use this to pick up info on admins who aren't currently in a channel.
        self.workers.defer(5, False, self.get_admins)
        extrachans = self.config['core']['extrachans']
        if extrachans:
            extrachans = [x.strip() for x in extrachans.split(',')]
            # Delay joining extra channels to prevent excess flood.
            for i, chan in enumerate(extrachans):
                self.workers.defer(i, False, self.connection.join, chan)

    def is_ignored(self, nick):
        with self.db.session_scope() as session:
            return session.query(orm.Ignore).filter(orm.Ignore.nick == nick).count()

    def get_filtered_send(self, cmdargs, send, target):
        """Parse out any filters."""
        parser = arguments.ArgParser(self.config)
        parser.add_argument('--filter')
        try:
            filterargs, remainder = parser.parse_known_args(cmdargs)
        except arguments.ArgumentException as ex:
            return str(ex), None
        cmdargs = ' '.join(remainder)
        if filterargs.filter is None:
            return cmdargs, send
        filter_list, output = textutils.append_filters(filterargs.filter)
        if filter_list is None:
            return output, None

        # define a new send to handle filter chaining
        def filtersend(msg, mtype='privmsg', target=target, ignore_length=False):
            self.send(target, self.connection.real_nickname, msg, mtype, ignore_length, filters=filter_list)
        return cmdargs, filtersend

    def do_rejoin(self, c, e):
        # If we're still banned, this will trigger a bannedfromchan event so we'll try again.
        if e.arguments[0] not in self.channels:
            c.join(e.arguments[0])

    def handle_event(self, msg, send, c, e):
        if e.type == 'whospcrpl':
            self.handle_who(e)
        elif e.type == 'account':
            self.handle_account(e)
        elif e.type == 'authenticate':
            self.handle_authenticate(e)
        elif e.type == 'bannedfromchan':
            self.workers.defer(5, False, self.do_rejoin, c, e)
        elif e.type == 'cap':
            self.handle_cap(e)
        elif e.type in ['ctcpreply', 'nosuchnick']:
            misc.ping(self.ping_map, c, e, datetime.now())
        elif e.type == 'error':
            logging.error(e.target)
        elif e.type == 'featurelist':
            if 'WHOX' in e.arguments:
                self.features['whox'] = True
        elif e.type == 'nick':
            self.handle_nick(send, e)
        elif e.type == 'nicknameinuse':
            self.connection.nick('Guest%d' % random.getrandbits(20))
        elif e.type == 'privnotice':
            if e.source.nick == 'NickServ':
                admin.set_admin(msg, self)
        elif e.type == 'welcome':
            self.handle_welcome()

    def handle_authenticate(self, e):
        passwd = self.config['auth']['serverpass']
        user = self.config['core']['nick']
        if e.target == '+':
            token = base64.b64encode('\0'.join([user, user, passwd]).encode())
            self.connection.send_raw('AUTHENTICATE %s' % token.decode())
            self.connection.cap('END')

    def handle_account(self, e):
        if e.source.nick in self.admins:
            if e.target == '*':
                self.admins[e.source.nick] = None
            else:
                self.admins[e.source.nick] = datetime.now()

    def handle_welcome(self):
        passwd = self.config['auth']['serverpass']
        user = self.config['core']['nick']
        logging.info("Connected to server %s", self.config['core']['host'])
        if self.config.getboolean('feature', 'nickserv') and self.connection.real_nickname != self.config['core']['nick']:
            self.connection.privmsg('NickServ', 'REGAIN %s %s' % (user, passwd))
        self.do_welcome()

    def handle_who(self, e):
        # arguments: type,nick,modes,account
        # properly track voiced status.
        location = self.who_map[int(e.arguments[0])]
        self.voiced[location][e.arguments[1]] = '+' in e.arguments[2]
        self.opers[location][e.arguments[1]] = '@' in e.arguments[2]
        if e.arguments[1] in self.admins:
            if e.arguments[3] != '0':
                self.admins[e.arguments[1]] = datetime.now()

    def handle_cap(self, e):
        if e.arguments[0] == 'ACK':
            if e.arguments[1].strip() == 'sasl':
                self.connection.send_raw('AUTHENTICATE PLAIN')
            elif e.arguments[1].strip() == 'account-notify':
                self.features['account-notify'] = True
            elif e.arguments[1].strip() == 'extended-join':
                self.features['extended-join'] = True

    def handle_nick(self, send, e):
        with self.data_lock:
            for channel in misc.get_channels(self.channels, e.target):
                self.do_log(channel, e.source.nick, e.target, 'nick')
                # Move the voice+op status to the new nick
                self.voiced[channel][e.target] = self.voiced[channel].pop(e.source.nick)
                self.opers[channel][e.target] = self.opers[channel].pop(e.source.nick)
        if identity.handle_nick(self, e):
            for x in misc.get_channels(self.channels, e.target):
                self.do_kick(send, x, e.target, "identity crisis")

    def handle_join(self, c, e, target, send):
        if self.features['whox']:
            tag = random.randint(0, 999)
            self.who_map[tag] = target
            if e.source.nick == c.real_nickname:
                # http://faerion.sourceforge.net/doc/irc/whox.var
                c.who('%s %%naft,%d' % (target, tag))
            else:
                c.who('%s %%naft,%d' % (e.source.nick, tag))
        if e.source.nick == c.real_nickname:
            send("Joined channel %s" % target, target=self.config['core']['ctrlchan'])
        elif self.features['extended-join']:
            if e.source.nick in self.admins:
                if e.arguments[0] == '*':
                    self.admins[e.source.nick] = None
                else:
                    self.admins[e.source.nick] = datetime.now()

    def get_cmd(self, msg):
        cmd = msg.split()[0]
        cmdchar = self.config['core']['cmdchar']

        cmdlen = len(cmd) + 1
        # FIXME: figure out a better way to handle !s
        if cmd.startswith('%ss' % cmdchar):
            # escape special regex chars
            raw_cmdchar = '\\' + cmdchar if re.match(r'[\[\].^$*+?]', cmdchar) else cmdchar
            match = re.match(r'%ss(\W)' % raw_cmdchar, cmd)
            if match:
                cmd = cmd.split(match.group(1))[0]
                cmdlen = len(cmd)

        cmdargs = msg[cmdlen:]
        cmd_name = cmd[len(cmdchar):].lower() if cmd.startswith(cmdchar) else None
        return cmd_name, cmdargs

    def run_cmd(self, send, nick, target, cmd_name, cmdargs, e):
        cmdargs, filtersend = self.get_filtered_send(cmdargs, send, target)
        if filtersend is None:
            send(cmdargs)
            return

        cmd_obj = command.registry.get_command(cmd_name)
        if cmd_obj.is_limited() and self.abusecheck(send, nick, target, cmd_obj.limit, cmd_name):
            return
        if cmd_obj.requires_admin() and not self.is_admin(send, nick):
            send("This command requires admin privileges.")
            return
        args = self.do_args(cmd_obj.args, send, nick, target, e.source, cmd_name, e.type)
        cmd_obj.run(filtersend, cmdargs, args, cmd_name, nick, target, self)

    def handle_kick(self, c, e, target, send):
        if e.arguments[0] == c.real_nickname:
            send("Kicked from channel %s" % target, target=self.config['core']['ctrlchan'])
            # Auto-rejoin after 5 seconds.
            self.workers.defer(5, False, self.connection.join, target)

    def handle_hooks(self, send, nick, target, e, msg):
        if self.config['feature'].getboolean('hooks'):
            for h in hook.registry.get_hook_objects():
                realargs = self.do_args(h.args, send, nick, target, e.source, h, e.type)
                h.run(send, msg, e.type, self, target, realargs)

    def handle_msg(self, c, e):
        """The Heart and Soul of IrcBot."""

        if e.type not in ['authenticate', 'error', 'join', 'part', 'quit']:
            nick = e.source.nick
        else:
            nick = e.source

        if e.arguments is None:
            msg = ""
        else:
            msg = " ".join(e.arguments).strip()

        # Send the response to private messages to the sending nick.
        target = nick if e.type == 'privmsg' else e.target

        def send(msg, mtype='privmsg', target=target, ignore_length=False):
            self.send(target, self.connection.real_nickname, msg, mtype, ignore_length)

        if e.type in ['account', 'authenticate', 'bannedfromchan', 'cap', 'ctcpreply', 'error', 'featurelist', 'nosuchnick', 'nick', 'nicknameinuse', 'privnotice', 'welcome', 'whospcrpl']:
            self.handle_event(msg, send, c, e)
            return

        # ignore empty messages
        if not msg and e.type != 'join':
            return

        self.do_log(target, nick, msg, e.type)

        if e.type == 'mode':
            self.do_mode(target, msg, nick, send)
            return

        if e.type == 'join':
            self.handle_join(c, e, target, send)
            return

        if e.type == 'part':
            if nick == c.real_nickname:
                send("Parted channel %s" % target, target=self.config['core']['ctrlchan'])
            return

        if e.type == 'kick':
            self.handle_kick(c, e, target, send)
            return

        if e.target == self.config['core']['ctrlchan'] and self.is_admin(None, nick):
            control.handle_ctrlchan(self, msg, send)

        if self.is_ignored(nick) and not self.is_admin(None, nick):
            return

        self.handle_hooks(send, nick, target, e, msg)

        msg = misc.get_cmdchar(self.config, c, msg, e.type)
        admins = [x.strip() for x in self.config['auth']['admins'].split(',')]
        cmd_name, cmdargs = self.get_cmd(msg)

        if command.registry.is_registered(cmd_name):
            self.run_cmd(send, nick, target, cmd_name, cmdargs, e)
        # special commands
        elif cmd_name == 'reload' and nick in admins:
            send("Aye Aye Capt'n")
