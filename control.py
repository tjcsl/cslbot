#!/usr/bin/python3 -O
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

import logging


def handle_chanserv(c, cmd, send):
    if len(cmd) < 3:
        send("Missing arguments.")
        return
    if cmd[1] == "op" or cmd[1] == "o":
        action = "OP %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
    elif cmd[1] == "deop" or cmd[1] == "do":
        action = "DEOP %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
    elif cmd[1] == "voice" or cmd[1] == "v":
        action = "VOICE %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
    elif cmd[1] == "devoice" or cmd[1] == "dv":
        action = "DEVOICE %s %s" % (cmd[2], cmd[3] if len(cmd) > 3 else "")
    c.privmsg("ChanServ", action)


def handle_disable(handler, cmd, send):
        if len(cmd) < 2:
            send("Missing argument.")
            return
        if cmd[1] == "kick":
            if not handler.kick_enabled:
                send("Kick already disabled.")
            else:
                handler.kick_enabled = False
                send("Kick disabled.")
        elif cmd[1] == "module":
            if len(cmd) < 3:
                send("Missing argument.")
                return
            if cmd[2] in handler.disabled_mods:
                send("Module already disabled.")
            elif cmd[2] in handler.modules:
                handler.disabled_mods.append(cmd[2])
                send("Module disabled.")
            else:
                send("Module does not exist.")
        elif cmd[1] == "logging":
            if logging.getLogger().getEffectiveLevel() == logging.INFO:
                send("logging already disabled.")
            else:
                logging.getLogger().setLevel(logging.INFO)
                send("Logging disabled.")
        elif cmd[1] == "chanlog":
            if handler.log_to_ctrlchan:
                handler.log_to_ctrlchan = False
                send("Control channel logging disabled.")
            else:
                send("Control channel logging is already disabled.")


def handle_enable(handler, cmd, send):
    if len(cmd) < 2:
        send("Missing argument.")
        return
    if cmd[1] == "kick":
        if handler.kick_enabled:
            send("Kick already enabled.")
        else:
            handler.kick_enabled = True
            send("Kick enabled.")
    elif cmd[1] == "module":
        if len(cmd) < 3:
            send("Missing argument.")
            return
        if cmd[2] in handler.modules:
            if cmd[2] in handler.disabled_mods:
                handler.disabled_mods.remove(cmd[2])
                send("Module enabled.")
            else:
                send("Module already enabled.")
        else:
            send("Module does not exist.")
    elif len(cmd) > 2 and cmd[1] == "all" and cmd[2] == "modules":
        handler.disabled_mods = []
        send("Enabled all modules.")
    elif cmd[1] == "logging":
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            send("logging already enabled.")
        else:
            logging.getLogger().setLevel(logging.DEBUG)
            send("Logging enabled.")
    elif cmd[1] == "chanlog":
        if not handler.log_to_ctrlchan:
            handler.log_to_ctrlchan = True
            send("Control channel logging enabled.")
        else:
            send("Control channel logging is already enabled.")


def handle_get(handler, cmd, send):
    if len(cmd) < 3:
        send("Missing argument.")
        return
    elif cmd[1] == "disabled" and cmd[2] == "modules":
        mods = ", ".join(sorted(handler.disabled_mods))
        if mods:
            send(mods)
        else:
            send("No disabled modules.")
    elif cmd[1] == "enabled" and cmd[2] == "modules":
        mods = ", ".join(sorted([i for i in handler.modules if i not in handler.disabled_mods]))
        send(mods)


def handle_guard(handler, cmd, send):
    if len(cmd) < 2:
        send("Missing argument.")
        return
    if cmd[1] in handler.guarded:
        send("already guarding " + cmd[1])
    else:
        handler.guarded.append(cmd[1])
        send("guarding " + cmd[1])


def handle_unguard(handler, cmd, send):
    if len(cmd) < 2:
        send("Missing argument.")
        return
    if cmd[1] not in handler.guarded:
        send("%s is not being guarded" % cmd[1])
    else:
        handler.guarded.remove(cmd[1])
        send("no longer guarding " + cmd[1])


def handle_show(handler, cmd, send):
    if len(cmd) < 2:
        send("Missing argument.")
        return
    if cmd[1] == "guarded":
        if handler.guarded:
            send(", ".join(handler.guarded))
        else:
            send("Nobody is guarded.")
    if cmd[1] == "issues":
        if handler.issues:
            for index, issue in enumerate(handler.issues):
                msg = "#%d %s -- by %s" % (index, issue[0], issue[1])
                send(msg)
        else:
            send("No outstanding issues.")


def handle_accept(handler, cmd, send):
    if len(cmd) < 2:
        send("Missing argument.")
        return
    if not cmd[1].isdigit():
        send("Not A Number")
    elif not handler.issues or len(handler.issues) < int(cmd[1]):
        send("Not a valid issue")
    else:
        num = int(cmd[1])
        msg, source = handler.issues[num]
        repo = handler.config.get('api', 'githubrepo')
        apikey = handler.config.get('api', 'githubapikey')
        issue = handler.modules['issue'].create_issue(msg, source, repo, apikey)
        handler.issues.pop(num)
        ctrlchan = handler.config.get('core', 'ctrlchan')
        channel = handler.config.get('core', 'channel')
        botnick = handler.config.get('core', 'nick')
        nick = source.split('!')[0]
        msg = "Issue Created -- %s -- %s" % (issue, msg)
        handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
        handler.do_log('private', botnick, msg, 'privmsg')


def handle_reject(handler, cmd, send):
    if len(cmd) < 2:
        send("Missing argument.")
        return
    if not cmd[1].isdigit():
        send("Not A Number")
    elif not handler.issues or len(handler.issues) < int(cmd[1]):
        send("Not a valid issue")
    else:
        msg, source = handler.issues.pop(int(cmd[1]))
        ctrlchan = handler.config.get('core', 'ctrlchan')
        channel = handler.config.get('core', 'channel')
        botnick = handler.config.get('core', 'nick')
        nick = source.split('!')[0]
        msg = "Issue Rejected -- %s" % msg
        handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
        handler.do_log('private', botnick, msg, 'privmsg')


def handle_quote(handler, cmd, send):
    if len(cmd) == 1:
        send("quote needs arguments.")
        return
    if cmd[1] == "join":
        send("quote join is not suported, use !join.")
        return
    handler.connection.send_raw(" ".join(cmd[1:]))


def handle_ctrlchan(handler, msg, c, send):
    """ Handle the control channel."""
    cmd = msg.split()
    if cmd[0] == "quote":
        handle_quote(handler, cmd, send)
    elif cmd[0] == "cs" or cmd[0] == "chanserv":
        handle_chanserv(c, cmd, send)
    elif cmd[0] == "disable":
        handle_disable(handler, cmd, send)
    elif cmd[0] == "enable":
        handle_enable(handler, cmd, send)
    elif cmd[0] == "get":
        handle_enable(handler, cmd, send)
    elif cmd[0] == "help":
        send("quote <raw command>")
        send("cs|chanserv <chanserv command>")
        send("disable|enable <kick|module <module>|logging|chanlog>")
        send("get <disabled|enabled> modules")
        send("show <guarded|issues>")
        send("accept|reject <issuenum>")
        send("guard|unguard <nick>")
    elif cmd[0] == "guard":
        handle_guard(handler, cmd, send)
    elif cmd[0] == "unguard":
        handle_unguard(handler, cmd, send)
    elif cmd[0] == "show":
        handle_show(handler, cmd, send)
    elif cmd[0] == "accept":
        handle_accept(handler, cmd, send)
    elif cmd[0] == "reject":
        handle_reject(handler, cmd, send)
