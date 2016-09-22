# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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
import configparser
import copy
import logging
import random
import re
import threading
import time
from datetime import datetime, timedelta

from irc import client, modes

from typing import Callable, Dict  # noqa

from . import acl, arguments, control, identity, misc, orm, registry, sql, textutils, workers

logger = logging.getLogger(__name__)


class BotHandler(object):

    def __init__(self, config: configparser.ConfigParser, connection: client.ServerConnection, channels: Dict[str, str], confdir: str) -> None:
        """Set everything up.

        | kick_enabled controls whether the bot will kick people or not.
        | abuselist is a dict keeping track of how many times nicks have used
        |   rate-limited commands.
        | modules is a dict containing the commands the bot supports.
        | confdir is the path to the directory where the bot's config is stored.
        | db - Is a db wrapper for data storage.

        """
        self.connection = connection  # type: client.ServerConnection
        self.channels = channels
        self.config = config  # type: configparser.ConfigParser
        self.db = sql.Sql(config, confdir)  # type: sql.Sql
        # FIXME: don't pass in self
        self.workers = workers.Workers(self)  # type: workers.Workers
        self.guarded = []  # type: List[str]
        self.voiced = collections.defaultdict(dict)  # type: Dict[str,Dict[str,bool]]
        self.opers = collections.defaultdict(dict)  # type: Dict[str,Dict[str,bool]]
        self.features = {'account-notify': False, 'extended-join': False, 'whox': False}
        start = datetime.now()
        self.uptime = {'start': start, 'reloaded': start}
        self.abuselist = {}  # type: Dict[str,Dict[str,datetime]]
        self.ping_map = {}  # type: Dict[str,str]
        self.outputfilter = collections.defaultdict(list)  # type: Dict[str,List[Callable[[str],str]]]
        self.kick_enabled = True
        self.who_map = {}  # type: Dict[int,str]
        self.flood_lock = threading.Lock()
        self.data_lock = threading.RLock()
        self.last_msg_time = datetime.now()
        self.confdir = confdir
        self.log_to_ctrlchan = False

    def get_data(self):
        """Saves the handler's data for :func:`.reloader.do_reload`"""
        data = {}
        data['guarded'] = self.guarded[:]
        data['voiced'] = copy.deepcopy(self.voiced)
        data['opers'] = copy.deepcopy(self.opers)
        data['features'] = self.features.copy()
        data['uptime'] = self.uptime.copy()
        data['abuselist'] = self.abuselist.copy()
        data['who_map'] = self.who_map.copy()
        return data

    def set_data(self, data):
        """Called from :func:`.reloader.do_reload` to restore the handler's data."""
        for key, val in data.items():
            setattr(self, key, val)
        self.uptime['reloaded'] = datetime.now()

    def update_authstatus(self, nick):
        if self.features['whox']:
            tag = random.randint(0, 999)
            self.who_map[tag] = nick
            self.send_who(nick, tag)
        elif self.config['feature']['servicestype'] == "ircservices":
            self.rate_limited_send('privmsg', 'NickServ', 'STATUS %s' % nick)
        elif self.config['feature']['servicestype'] == "atheme":
            self.rate_limited_send('privmsg', 'NickServ', 'ACC %s' % nick)

    def send_who(self, target, tag):
        # http://faerion.sourceforge.net/doc/irc/whox.var
        # n(show nicknames), a(show nickserv status), f(show channel status/modes), t(show tag)
        self.rate_limited_send('who', '%s %%naft,%d' % (target, tag))

    def is_admin(self, send, nick):
        """Checks if a nick is a admin.

        If NickServ hasn't responded yet, then the admin is unverified,
        so assume they aren't a admin.

        """
        # Current roles are admin and owner, which is a superset of admin.
        with self.db.session_scope() as session:
            admin = session.query(orm.Permissions).filter(orm.Permissions.nick == nick).first()
            if admin is None:
                return False
            # no nickserv support, assume people are who they say they are.
            if not self.config['feature'].getboolean('nickserv'):
                return True
            if not admin.registered:
                self.update_authstatus(nick)
                # We don't necessarily want to complain in all cases.
                if send is not None:
                    send("Unverified admin: %s" % nick, target=self.config['core']['channel'])
                return False
            else:
                if not self.features['account-notify']:
                    # reverify every 5min if we don't have the notification feature.
                    if datetime.now() - admin.time > timedelta(minutes=5):
                        self.update_authstatus(nick)
                return True

    def get_admins(self):
        """Check verification for all admins."""
        # no nickserv support, assume people are who they say they are.
        if not self.config['feature'].getboolean('nickserv'):
            return
        with self.db.session_scope() as session:
            for a in session.query(orm.Permissions).all():
                if not a.registered:
                    self.update_authstatus(a.nick)

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
    def get_max_length(target: str, msgtype: str) -> int:
        overhead = r"PRIVMSG %s: \r\n" % target
        # FIXME: what the hell is up w/ message length limits?
        if msgtype == 'action':
            overhead += "\001ACTION \001"
            max_len = 454  # 512
        else:
            max_len = 453  # 512
        return max_len - len(overhead.encode())

    def send(self, target, nick, msg: str, msgtype, ignore_length=False, filters=None):
        """Send a message.

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
        msg_enc = [x.encode() for x in msg]
        if sum(map(len, msg_enc)) > max_len and not ignore_length:
            msg, _ = misc.split_msg(msg_enc, max_len)
            msg += "..."
            msg_enc = [x.encode() for x in msg]
        max_len = self.get_max_length(target, msgtype)
        # We can't send messages > 512 bytes to irc.
        while sum(map(len, msg_enc)) > max_len:
            split, msg_enc = misc.split_msg(msg_enc, max_len)
            msgs.append(split)
        msgs.append(''.join([x.decode() for x in msg_enc]).strip())
        for i in msgs:
            self.do_log(target, nick, i, msgtype)
            if msgtype == 'action':
                self.rate_limited_send('action', target, i)
            else:
                self.rate_limited_send('privmsg', target, i)

    def rate_limited_send(self, mtype: str, target: str, msg: str = None) -> None:
        with self.flood_lock:
            elapsed = datetime.now() - self.last_msg_time
            # Don't send messages more then once every 0.5 sec.
            time.sleep(max(0, 0.5 - elapsed.total_seconds()))
            if msg is None:
                getattr(self.connection, mtype)(target)
            else:
                getattr(self.connection, mtype)(target, msg)
            self.last_msg_time = datetime.now()

    def do_log(self, target: str, nick: str, msg: str, msgtype: str) -> None:
        """Handles logging.

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
                if self.opers[target].get(nick, False):
                    flags |= 1
                if self.voiced[target].get(nick, False):
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
        """Leaves a channel.

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
        """Join a channel.

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
            send("%s is already a member of %s" % (self.config['core']['nick'], cmd[0]))
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
        """reop and handle guard violations."""
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
        """Kick users.

        - If kick is disabled, don't do anything.
        - If the bot is not a op, rage at a op.
        - Kick the user.

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
        """Handle the various args that modules need."""
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

        - Join the primary channel.
        - Join the control channel.

        """
        self.rate_limited_send('join', self.config['core']['channel'])
        self.rate_limited_send('join', self.config['core']['ctrlchan'], self.config['auth']['ctrlkey'])
        # We use this to pick up info on admins who aren't currently in a channel.
        self.workers.defer(5, False, self.get_admins)
        extrachans = self.config['core']['extrachans']
        if extrachans:
            for chan in [x.strip() for x in extrachans.split(',')]:
                self.rate_limited_send('join', chan)

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
            logger.error(e.target)
        elif e.type == 'featurelist':
            if 'WHOX' in e.arguments:
                self.features['whox'] = True
        elif e.type == 'nick':
            self.handle_nick(send, e)
        elif e.type == 'nicknameinuse':
            self.connection.nick('Guest%d' % random.getrandbits(20))
        elif e.type == 'privnotice':
            if e.source.nick == 'NickServ':
                # FIXME: don't pass self
                acl.set_admin(msg, self)
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
        with self.db.session_scope() as session:
            admin = session.query(orm.Permissions).filter(orm.Permissions.nick == e.source.nick).first()
            if admin is not None:
                if e.target == '*':
                    admin.registered = False
                else:
                    admin.registered = True
                    admin.time = datetime.now()

    def handle_welcome(self):
        passwd = self.config['auth']['serverpass']
        user = self.config['core']['nick']
        logger.info("Connected to server %s", self.config['core']['host'])
        if self.config.getboolean('feature', 'nickserv') and self.connection.real_nickname != self.config['core']['nick']:
            self.connection.privmsg('NickServ', 'REGAIN %s %s' % (user, passwd))
        self.do_welcome()

    def handle_who(self, e):
        # arguments: tag,nick,modes,account
        # modes = H(here) or G(away), +(voice), @(oper)
        # account is the nicksev account if authed, else 0
        # properly track voiced status.
        location = self.who_map[int(e.arguments[0])]
        # FIXME: devoice if G in modes
        self.voiced[location][e.arguments[1]] = '+' in e.arguments[2]
        self.opers[location][e.arguments[1]] = '@' in e.arguments[2]
        with self.db.session_scope() as session:
            admin = session.query(orm.Permissions).filter(orm.Permissions.nick == e.arguments[1]).first()
            if admin is not None:
                if e.arguments[3] != '0':
                    admin.registered = True
                    admin.time = datetime.now()

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
                if e.source.nick in self.voiced[channel].keys():  # In case we somehow didn't set the voice state on the old nick
                    self.voiced[channel][e.target] = self.voiced[channel].pop(e.source.nick)
                if e.source.nick in self.opers[channel].keys():  # As above, for ops
                    self.opers[channel][e.target] = self.opers[channel].pop(e.source.nick)
        if identity.handle_nick(self, e):
            for x in misc.get_channels(self.channels, e.target):
                self.do_kick(send, x, e.target, "identity crisis")

    def handle_join(self, c, e, target, send):
        # Get status for all nicks in-channel when we join, or the new nick when somebody else joins.
        if self.features['whox']:
            tag = random.randint(0, 999)
            self.who_map[tag] = target
            if e.source.nick == c.real_nickname:
                self.send_who(target, tag)
            else:
                self.send_who(e.source.nick, tag)
        if e.source.nick == c.real_nickname:
            send("Joined channel %s" % target, target=self.config['core']['ctrlchan'])
        elif self.features['extended-join']:
            with self.db.session_scope() as session:
                admin = session.query(orm.Permissions).filter(orm.Permissions.nick == e.source.nick).first()
                if admin is not None:
                    if e.arguments[0] == '*':
                        admin.registered = False
                    else:
                        admin.registered = True
                        admin.time = datetime.now()

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

        cmd_obj = registry.command_registry.get_command(cmd_name)
        if cmd_obj.is_limited() and self.abusecheck(send, nick, target, cmd_obj.limit, cmd_name):
            return
        with self.db.session_scope() as session:
            if not cmd_obj.has_role(session, nick):
                send("Insufficent privileges for command.")
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
            for h in registry.hook_registry.get_hook_objects():
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

        if e.type in ['account', 'authenticate', 'bannedfromchan', 'cap', 'ctcpreply', 'error', 'featurelist', 'nosuchnick', 'nick', 'nicknameinuse',
                      'privnotice', 'welcome', 'whospcrpl']:
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
        cmd_name, cmdargs = self.get_cmd(msg)

        if registry.command_registry.is_registered(cmd_name):
            self.run_cmd(send, nick, target, cmd_name, cmdargs, e)
        # special commands
        elif cmd_name == 'reload':
            with self.db.session_scope() as session:
                if session.query(orm.Permissions).filter(orm.Permissions.nick == nick).count():
                    send("Aye Aye Capt'n")
