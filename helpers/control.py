#!/usr/bin/python3 -O
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from . import command
from .orm import Quotes, Issues, Polls
from commands.issue import create_issue


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
    else:
        send("Invalid action.")
        return
    send(action, target="ChanServ")


def handle_disable(handler, cmd):
        if len(cmd) < 2:
            return "Missing argument."
        if cmd[1] == "kick":
            if not handler.kick_enabled:
                return "Kick already disabled."
            else:
                handler.kick_enabled = False
                return "Kick disabled."
        elif cmd[1] == "module":
            if len(cmd) < 3:
                return "Missing argument."
            return command.disable_command(cmd[2])
        elif cmd[1] == "logging":
            if logging.getLogger().getEffectiveLevel() == logging.INFO:
                return "logging already disabled."
            else:
                logging.getLogger().setLevel(logging.INFO)
                return "Logging disabled."
        elif cmd[1] == "chanlog":
            if handler.log_to_ctrlchan:
                handler.log_to_ctrlchan = False
                return "Control channel logging disabled."
            else:
                return "Control channel logging is already disabled."
        else:
            return "Invalid argument."


def handle_enable(handler, cmd):
    if len(cmd) < 2:
        return "Missing argument."
    if cmd[1] == "kick":
        if handler.kick_enabled:
            return "Kick already enabled."
        else:
            handler.kick_enabled = True
            return "Kick enabled."
    elif cmd[1] == "module":
        if len(cmd) < 3:
            return "Missing argument."
        return command.enable_command(cmd[2])
    elif len(cmd) > 2 and cmd[1] == "all" and cmd[2] == "modules":
        return command.enable_command(cmd[1])
    elif cmd[1] == "logging":
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            return "logging already enabled."
        else:
            logging.getLogger().setLevel(logging.DEBUG)
            return "Logging enabled."
    elif cmd[1] == "chanlog":
        if not handler.log_to_ctrlchan:
            handler.log_to_ctrlchan = True
            return "Control channel logging enabled."
        else:
            return "Control channel logging is already enabled."
    else:
        return "Invalid argument."


def handle_get(handler, cmd):
    if len(cmd) < 3:
        return "Missing argument."
    elif cmd[1] == "disabled" and cmd[2] == "modules":
        mods = ", ".join(sorted(command.get_disabled_commands()))
        return mods if mods else "No disabled modules."
    elif cmd[1] == "enabled" and cmd[2] == "modules":
        mods = ", ".join(sorted(command.get_enabled_commands()))
        return mods
    else:
        return "Invalid arguments."


def handle_guard(handler, cmd):
    if len(cmd) < 2:
        return "Missing argument."
    if cmd[1] in handler.guarded:
        return "Already guarding " + cmd[1]
    else:
        handler.guarded.append(cmd[1])
        return "Guarding " + cmd[1]


def handle_unguard(handler, cmd):
    if len(cmd) < 2:
        return "Missing argument."
    if cmd[1] not in handler.guarded:
        return "%s is not being guarded" % cmd[1]
    else:
        handler.guarded.remove(cmd[1])
        return "No longer guarding %s" % cmd[1]


def handle_show(handler, cmd, send):
    db = handler.db.get()
    if len(cmd) < 2:
        send("Missing argument.")
        return
    elif cmd[1] == "guarded":
        if handler.guarded:
            send(", ".join(handler.guarded))
        else:
            send("Nobody is guarded.")
    elif cmd[1] == "issues":
        issues = db.query(Issues).filter(Issues.accepted == 0).all()
        if issues:
            show_issues(issues, send)
        else:
            send("No outstanding issues.")
    elif cmd[1] == "quotes":
        quotes = db.query(Quotes).filter(Quotes.approved == 0).all()
        if quotes:
            show_quotes(quotes, send)
        else:
            send("No quotes pending.")
    elif cmd[1] == "polls":
        polls = db.query(Polls).filter(Polls.accepted == 0).all()
        if polls:
            show_polls(polls, send)
        else:
            send("No polls pending.")
    elif cmd[1] == "pending":
        admins = ": ".join(handler.admins)
        show_pending(db, admins, send)
    else:
        send("Invalid Argument.")


def show_quotes(quotes, send):
    for x in quotes:
        send("#%d %s -- %s, Submitted by %s" % (x.id, x.quote, x.nick, x.submitter))


def show_issues(issues, send):
    for issue in issues:
        nick = issue.source.split('!')[0]
        send("#%d %s, Submitted by %s" % (issue.id, issue.title, nick))


def show_polls(polls, send):
    for x in polls:
        send("#%d -- %s, Submitted by %s" % (x.id, x.question, x.submitter))


def show_pending(db, admins, send, ping=False):
        issues = db.query(Issues).filter(Issues.accepted == 0).all()
        quotes = db.query(Quotes).filter(Quotes.approved == 0).all()
        polls = db.query(Polls).filter(Polls.accepted == 0).all()
        if ping:
            if issues or quotes or polls:
                send("%s: Items are Pending Approval" % admins)
            else:
                send("No items are Pending")
        if issues:
            send("Issues:")
            show_issues(issues, send)
        if quotes:
            send("Quotes:")
            show_quotes(quotes, send)
        if polls:
            send("Polls:")
            show_polls(polls, send)


def handle_accept(handler, cmd):
    if len(cmd) < 3:
        return "Missing argument."
    if cmd[1] == 'issue':
        return accept_issue(handler, cmd[1:])
    elif cmd[1] == 'quote':
        return accept_quote(handler, cmd[1:])
    elif cmd[1] == 'poll':
        return accept_poll(handler, cmd[1:])
    else:
        return "Valid arguments are issue and quote"


def accept_issue(handler, cmd):
    if not cmd[1].isdigit():
        return "Not A Valid Positive Integer"
    db = handler.db.get()
    num = int(cmd[1])
    issue = db.query(Issues).get(num)
    if issue is None:
        return "Not a valid issue"
    repo = handler.config['api']['githubrepo']
    apikey = handler.config['api']['githubapikey']
    msg = create_issue(issue.title, issue.source, repo, apikey)
    issue.accepted = 1
    ctrlchan = handler.config['core']['ctrlchan']
    channel = handler.config['core']['channel']
    botnick = handler.config['core']['nick']
    nick = issue.source.split('!')[0]
    msg = "Issue Created -- %s -- %s" % (msg, issue.title)
    handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
    handler.do_log('private', botnick, msg, 'privmsg')
    return ""


def accept_quote(handler, cmd):
    if not cmd[1].isdigit():
        return "Not A Valid Positive Integer"
    db = handler.db.get()
    qid = int(cmd[1])
    quote = db.query(Quotes).get(qid)
    if quote is None:
        return "Not a valid quote"
    quote.approved = 1
    ctrlchan = handler.config['core']['ctrlchan']
    channel = handler.config['core']['channel']
    botnick = handler.config['core']['nick']
    nick = quote.submitter
    msg = "Quote #%d Accepted: %s -- %s, Submitted by %s" % (qid, quote.quote, quote.nick, nick)
    handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
    handler.do_log('private', botnick, msg, 'privmsg')
    return ""


def accept_poll(handler, cmd):
    if not cmd[1].isdigit():
        return "Not A Valid Positive Integer"
    db = handler.db.get()
    pid = int(cmd[1])
    poll = db.query(Polls).get(pid)
    if poll is None:
        return "Not a valid poll"
    poll.accepted = 1
    ctrlchan = handler.config['core']['ctrlchan']
    channel = handler.config['core']['channel']
    botnick = handler.config['core']['nick']
    nick = poll.submitter
    msg = "Poll #%d accepted: %s , Submitted by %s" % (id, poll.question, nick)
    handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
    handler.do_log('private', botnick, msg, 'privmsg')
    return ""


def handle_reject(handler, cmd):
    if len(cmd) < 3:
        return "Missing argument."
    if cmd[1] == 'issue':
        return reject_issue(handler, cmd[1:])
    elif cmd[1] == 'quote':
        return reject_quote(handler, cmd[1:])
    elif cmd[1] == 'poll':
        return reject_poll(handler, cmd[1:])
    else:
        return "Valid arguments are issue and quote"


def reject_issue(handler, cmd):
    if not cmd[1].isdigit():
        return "Not A Valid Positive Integer"
    db = handler.db.get()
    num = int(cmd[1])
    issue = db.query(Issues).get(num)
    if issue is None:
        return "Not a valid issue"
    ctrlchan = handler.config['core']['ctrlchan']
    channel = handler.config['core']['channel']
    botnick = handler.config['core']['nick']
    nick = issue.source.split('!')[0]
    msg = "Issue Rejected -- %s, Submitted by %s" % (issue.title, nick)
    handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
    handler.do_log('private', botnick, msg, 'privmsg')
    db.delete(issue)
    return ""


def reject_quote(handler, cmd):
    if not cmd[1].isdigit():
        return "Not A Valid Positive Integer"
    db = handler.db.get()
    qid = int(cmd[1])
    quote = db.query(Quotes).get(qid)
    if quote is None:
        return "Not a valid quote"
    if quote.approved == 1:
        return "Quote already approved."
    ctrlchan = handler.config['core']['ctrlchan']
    channel = handler.config['core']['channel']
    botnick = handler.config['core']['nick']
    nick = quote.submitter
    msg = "Quote #%d Rejected: %s -- %s, Submitted by %s" % (qid, quote.quote, quote.nick, nick)
    db.delete(quote)
    handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
    handler.do_log('private', botnick, msg, 'privmsg')
    return ""


def reject_poll(handler, cmd):
    if not cmd[1].isdigit():
        return "Not A Valid Positive Integer"
    db = handler.db.get()
    pid = int(cmd[1])
    poll = db.query(Polls).get(pid)
    if poll is None:
        return "Not a valid poll"
    ctrlchan = handler.config['core']['ctrlchan']
    channel = handler.config['core']['channel']
    botnick = handler.config['core']['nick']
    nick = poll.submitter
    msg = "Poll #%d rejected: %s, Submitted by %s" % (pid, poll.question, nick)
    handler.connection.privmsg_many([ctrlchan, channel, nick], msg)
    handler.do_log('private', botnick, msg, 'privmsg')
    db.delete(poll)
    return ""


def handle_quote(handler, cmd):
    if len(cmd) == 1:
        return "quote needs arguments."
    if cmd[1] == "join":
        return "quote join is not suported, use !join."
    handler.connection.send_raw(" ".join(cmd[1:]))
    return ""


def handle_ctrlchan(handler, msg, c, send):
    """ Handle the control channel."""
    cmd = msg.split()
    if cmd[0] == "quote":
        send(handle_quote(handler, cmd))
    elif cmd[0] == "cs" or cmd[0] == "chanserv":
        handle_chanserv(c, cmd, send)
    elif cmd[0] == "disable":
        send(handle_disable(handler, cmd))
    elif cmd[0] == "enable":
        send(handle_enable(handler, cmd))
    elif cmd[0] == "get":
        send(handle_get(handler, cmd))
    elif cmd[0] == "help":
        send("quote <raw command>")
        send("cs|chanserv <chanserv command>")
        send("disable|enable <kick|module <module>|all modules|logging|chanlog>")
        send("get <disabled|enabled> modules")
        send("show <guarded|issues|quotes|polls>")
        send("accept|reject <issue|quote|poll> <num>")
        send("guard|unguard <nick>")
    elif cmd[0] == "guard":
        send(handle_guard(handler, cmd))
    elif cmd[0] == "unguard":
        send(handle_unguard(handler, cmd))
    elif cmd[0] == "show":
        handle_show(handler, cmd, send)
    elif cmd[0] == "accept":
        send(handle_accept(handler, cmd))
    elif cmd[0] == "reject":
        send(handle_reject(handler, cmd))
