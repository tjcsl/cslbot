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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import re
import logging
from . import command, orm, hook, arguments, web
from .orm import Quotes, Issues, Polls, Tumblrs


def handle_chanserv(args):
    args.send("%s %s" % (args.cmd, " ".join(args.args)), target="ChanServ")


def toggle_logging(level):
    if logging.getLogger().getEffectiveLevel() == level:
        return False
    else:
        logging.getLogger().setLevel(level)
        return True


def handle_disable(args):
    if args.cmd == "kick":
        if not args.handler.kick_enabled:
            args.send("Kick already disabled.")
        else:
            args.handler.kick_enabled = False
            args.send("Kick disabled.")
    elif args.cmd == "command":
        if args.args:
            args.send(command.disable_command(args.args[0]))
        else:
            args.send("Missing argument.")
    elif args.cmd == "hook":
        if args.args:
            args.send(hook.disable_hook(args.args[0]))
        else:
            args.send("Missing argument.")
    elif args.cmd == "logging":
        if toggle_logging(logging.INFO):
            args.send("Logging disabled.")
        else:
            args.send("logging already disabled.")
    elif args.cmd == "chanlog":
        if args.handler.log_to_ctrlchan:
            args.handler.log_to_ctrlchan = False
            args.send("Control channel logging disabled.")
        else:
            args.send("Control channel logging is already disabled.")


def handle_enable(args):
    if args.cmd == "kick":
        if args.handler.kick_enabled:
            args.send("Kick already enabled.")
        else:
            args.handler.kick_enabled = True
            args.send("Kick enabled.")
    elif args.cmd == "command":
        if args.args:
            args.send(command.enable_command(args.args[0]))
        else:
            args.send("Missing argument.")
    elif args.cmd == "all":
        if not args.args:
            args.send("Missing argument.")
        elif args.args[0] == "commands":
            args.send(command.enable_command(args.cmd))
        elif args.args[0] == "hooks":
            args.send(hook.enable_hook(args.cmd))
        else:
            args.send("Invalid argument.")
    elif args.cmd == "hook":
        if args.args:
            args.send(hook.enable_hook(args.args[0]))
        else:
            args.send("Missing argument.")
    elif args.cmd == "logging":
        if toggle_logging(logging.DEBUG):
            args.send("Logging enabled.")
        else:
            args.send("logging already enabled.")
    elif args.cmd == "chanlog":
        if not args.handler.log_to_ctrlchan:
            args.handler.log_to_ctrlchan = True
            args.send("Control channel logging enabled.")
        else:
            args.send("Control channel logging is already enabled.")


def handle_guard(args):
    if args.nick in args.handler.guarded:
        args.send("Already guarding %s" % args.nick)
    else:
        args.handler.guarded.append(args.nick)
        args.send("Guarding %s" % args.nick)


def handle_unguard(args):
    if args.nick not in args.handler.guarded:
        args.send("%s is not being guarded" % args.nick)
    else:
        args.handler.guarded.remove(args.nick)
        args.send("No longer guarding %s" % args.nick)


def handle_show(args):
    if args.cmd == "guarded":
        if args.handler.guarded:
            args.send(", ".join(args.handler.guarded))
        else:
            args.send("Nobody is guarded.")
    elif args.cmd == "issues":
        issues = args.db.query(Issues).filter(Issues.accepted == 0).all()
        if issues:
            show_issues(issues, args.send)
        else:
            args.send("No outstanding issues.")
    elif args.cmd == "quotes":
        quotes = args.db.query(Quotes).filter(Quotes.accepted == 0).all()
        if quotes:
            show_quotes(quotes, args.send)
        else:
            args.send("No quotes pending.")
    elif args.cmd == "polls":
        polls = args.db.query(Polls).filter(Polls.accepted == 0).all()
        if polls:
            show_polls(polls, args.send)
        else:
            args.send("No polls pending.")
    elif args.cmd == "pending":
        if args.args:
            args.send("Invalid argument %s." % args.args[0])
        else:
            admins = ": ".join(args.handler.admins)
            show_pending(args.db, admins, args.send)
    elif args.cmd == "enabled":
        if not args.args:
            args.send("Missing argument.")
        elif args.args[0] == "commands":
            mods = ", ".join(sorted(command.get_enabled_commands()))
            args.send(mods, ignore_length=True)
        elif args.args[0] == "hooks":
            mods = ", ".join(sorted(hook.get_enabled_hooks()))
            args.send(mods)
        else:
            args.send("Invalid argument.")
    elif args.cmd == "disabled":
        if not args.args:
            args.send("Missing argument.")
        elif args.args[0] == "commands":
            mods = ", ".join(sorted(command.get_disabled_commands()))
            args.send(mods if mods else "No disabled commands.")
        elif args.args[0] == "hooks":
            mods = ", ".join(sorted(hook.get_disabled_hooks()))
            args.send(mods if mods else "No disabled hooks.")
        else:
            args.send("Invalid argument.")
    elif args.cmd == "tumblr":
        tumblrs = args.db.query(Tumblrs).filter(Tumblrs.accepted == 0).all()
        if tumblrs:
            show_tumblrs(tumblrs, args.send)
        else:
            args.send("No Tumblr posts pending")


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


def show_tumblrs(tumblrs, send):
    for x in tumblrs:
        send("#%d -- %s for %s, Submitted by %s" % (x.id, x.post, x.blogname, x.submitter))


def show_pending(db, admins, send, ping=False):
    issues = db.query(Issues).filter(Issues.accepted == 0).all()
    quotes = db.query(Quotes).filter(Quotes.accepted == 0).all()
    polls = db.query(Polls).filter(Polls.accepted == 0).all()
    tumblrs = db.query(Tumblrs).filter(Tumblrs.accepted == 0).all()
    if issues or quotes or polls:
        if ping:
            send("%s: Items are Pending Approval" % admins)
    elif not ping:
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
    if tumblrs:
        send("Tumblr posts:")
        show_tumblrs(tumblrs, send)


def handle_accept(args):
    table = getattr(orm, args.cmd.capitalize())
    pending = args.db.query(table).filter(table.accepted == 0, table.id == args.num).first()
    if pending is None:
        args.send("Not a valid %s" % args.cmd)
        return
    msg, success = get_accept_msg(args.handler, pending, args.cmd)
    if not success:
        args.send(msg)
        return
    pending.accepted = 1
    ctrlchan = args.handler.config['core']['ctrlchan']
    channel = args.handler.config['core']['channel']
    botnick = args.handler.config['core']['nick']
    args.handler.connection.privmsg_many([ctrlchan, channel, pending.submitter], msg)
    args.handler.do_log('private', botnick, msg, 'privmsg')


def get_accept_msg(handler, pending, type):
    success = True
    if type == 'quote':
        msg = "Quote #%d Accepted: %s -- %s, Submitted by %s" % (pending.id, pending.quote, pending.nick, pending.submitter)
    elif type == 'poll':
        msg = "Poll #%d accepted: %s, Submitted by %s" % (pending.id, pending.question, pending.submitter)
    elif type == 'issue':
        repo = handler.config['api']['githubrepo']
        apikey = handler.config['api']['githubapikey']
        msg, success = web.create_issue(pending.title, pending.description, pending.source, repo, apikey)
        if success:
            msg = "Issue Created -- %s -- %s" % (msg, pending.title)
    elif type == 'tumblr':
        msg, success = web.post_tumblr(handler.config, pending.blog, pending.post)
        if success:
            msg = "Tumblr post #%d accepted: %s, Submitted by %s" % (pending.id, pending.post, pending.submitter)
    return msg, success


def handle_reject(args):
    table = getattr(orm, args.cmd.capitalize())
    pending = args.db.query(table).get(args.num)
    if pending is None:
        args.send("Not a valid %s" % args.cmd)
        return
    if pending.accepted == 1:
        args.send("%s already accepted" % args.cmd.capitialize())
        return
    ctrlchan = args.handler.config['core']['ctrlchan']
    channel = args.handler.config['core']['channel']
    botnick = args.handler.config['core']['nick']
    msg = get_reject_msg(args.cmd)
    args.handler.connection.privmsg_many([ctrlchan, channel, pending.submitter], msg)
    args.handler.do_log('private', botnick, msg, 'privmsg')
    args.db.delete(pending)


def get_reject_msg(pending, type):
    if type == 'issue':
        nick = pending.source.split('!')[0]
        return "Issue Rejected -- %s, Submitted by %s" % (pending.title, nick)
    elif type == 'quote':
        return "Quote #%d Rejected: %s -- %s, Submitted by %s" % (pending.id, pending.quote, pending.nick, pending.submitter)
    elif type == 'poll':
        return "Poll #%d rejected: %s, Submitted by %s" % (pending.id, pending.question, pending.submitter)
    elif type == 'tumblr':
        return "Tumblr #%d rejected: %s, Submitted by %s" % (pending.id, pending.post, pending.submitter)


def handle_quote(args):
    if args.cmd[0] == "join":
        args.send("quote join is not suported, use !join.")
    else:
        args.handler.connection.send_raw(" ".join(args.cmd))


def handle_help(args):
    args.send("quote <raw command>")
    args.send("cs|chanserv <chanserv command>")
    args.send("disable|enable <kick|command <command>|hook <hook>|all <commands|hooks>|logging|chanlog>")
    args.send("show <guarded|issues|quotes|polls|pending|tumblr> <disabled|enabled> <commands|hooks>")
    args.send("accept|reject <issue|quote|poll> <num>")
    args.send("guard|unguard <nick>")


def init_parser(send, handler, db):
    parser = arguments.ArgParser(handler.config)
    parser.set_defaults(send=send, handler=handler, db=db)
    subparser = parser.add_subparsers()

    quote_parser = subparser.add_parser('quote')
    quote_parser.add_argument('cmd', nargs='+')
    quote_parser.set_defaults(func=handle_quote)

    help_parser = subparser.add_parser('help')
    help_parser.set_defaults(func=handle_help)

    cs_parser = subparser.add_parser('chanserv', aliases=['cs'])
    cs_parser.add_argument('cmd', choices=['op', 'deop', 'voice', 'devoice'])
    cs_parser.add_argument('args', nargs='+')
    cs_parser.set_defaults(func=handle_chanserv)

    disable_parser = subparser.add_parser('disable')
    disable_parser.add_argument('cmd', choices=['kick', 'command', 'hook', 'logging', 'chanlog'])
    disable_parser.add_argument('args', nargs='*')
    disable_parser.set_defaults(func=handle_disable)

    enable_parser = subparser.add_parser('enable')
    enable_parser.add_argument('cmd', choices=['kick', 'command', 'hook', 'logging', 'chanlog', 'all'])
    enable_parser.add_argument('args', nargs='*')
    enable_parser.set_defaults(func=handle_enable)

    guard_parser = subparser.add_parser('guard')
    guard_parser.add_argument('nick', action=arguments.NickParser)
    guard_parser.set_defaults(func=handle_guard)

    unguard_parser = subparser.add_parser('unguard')
    unguard_parser.add_argument('nick', action=arguments.NickParser)
    unguard_parser.set_defaults(func=handle_unguard)

    # We need the config in the guard_parser and unguard_parser namespaces but there's no way to pass arbitrary
    # arguments to subparser.add_parser, and now way to talk to the parent parser from subparsers. Thus, we must
    # fall back on hacky crap like this
    guard_parser.namespace.config = handler.config
    unguard_parser.namespace.config = handler.config

    show_parser = subparser.add_parser('show')
    show_parser.add_argument('cmd', choices=['guarded', 'issues', 'quotes', 'polls', 'pending', 'disabled', 'enabled'])
    show_parser.add_argument('args', nargs='*')
    show_parser.set_defaults(func=handle_show)

    show_parser = subparser.add_parser('accept')
    show_parser.add_argument('cmd', choices=['issue', 'quote', 'poll'])
    show_parser.add_argument('num', type=int)
    show_parser.set_defaults(func=handle_accept)

    show_parser = subparser.add_parser('reject')
    show_parser.add_argument('cmd', choices=['issue', 'quote', 'poll'])
    show_parser.add_argument('num', type=int)
    show_parser.set_defaults(func=handle_reject)

    return parser


def handle_ctrlchan(handler, msg, send):
    """ Handle the control channel."""
    with handler.db.session_scope() as db:
        parser = init_parser(send, handler, db)
        try:
            cmdargs = parser.parse_args(msg)
        except arguments.ArgumentException as e:
            # FIXME: figure out a better way to allow non-commands without spamming the channel.
            err_str = r"invalid choice: .* \(choose from 'quote', 'help', 'chanserv', 'cs', 'disable', 'enable', 'guard', 'unguard', 'show', 'accept', 'reject'\)"
            if not re.match(err_str, str(e)):
                send(str(e))
            return
        cmdargs.func(cmdargs)
