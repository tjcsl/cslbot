# -*- coding: utf-8 -*-
# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import collections

from ..helpers import arguments
from ..helpers.command import Command
from ..helpers.orm import Poll_responses, Polls


def start_poll(args):
    """Starts a poll."""
    if args.type == 'privmsg':
        return "We don't have secret ballots in this benevolent dictatorship!"
    if not args.msg:
        return "Polls need a question."
    ctrlchan = args.config['core']['ctrlchan']
    poll = Polls(question=args.msg, submitter=args.nick)
    args.session.add(poll)
    args.session.flush()
    if args.isadmin:
        poll.accepted = 1
        return "Poll #%d created!" % poll.id
    else:
        args.send("Poll submitted for approval.", target=args.nick)
        args.send("New Poll: #%d -- %s, Submitted by %s" % (poll.id, args.msg, args.nick), target=ctrlchan)
        return ""


def delete_poll(args):
    """Deletes a poll."""
    if not args.isadmin:
        return "Nope, not gonna do it."
    if not args.msg:
        return "Syntax: !poll delete <pollnum>"
    if not args.msg.isdigit():
        return "Not A Valid Positive Integer."
    poll = args.session.query(Polls).filter(Polls.accepted == 1, Polls.id == int(args.msg)).first()
    if poll is None:
        return "Poll does not exist."
    if poll.active == 1:
        return "You can't delete an active poll!"
    elif poll.deleted == 1:
        return "Poll already deleted."
    poll.deleted = 1
    return "Poll deleted."


def get_open_poll(session, pid):
    return session.query(Polls).filter(Polls.deleted == 0, Polls.accepted == 1, Polls.id == pid).first()


def edit_poll(args):
    """Edits a poll."""
    if not args.isadmin:
        return "Nope, not gonna do it."
    msg = args.msg.split(maxsplit=1)
    if len(msg) < 2:
        return "Syntax: !vote edit <pollnum> <question>"
    if not msg[0].isdigit():
        return "Not A Valid Positive Integer."
    pid = int(msg[0])
    poll = get_open_poll(args.session, pid)
    if poll is None:
        return "That poll was deleted or does not exist!"
    poll.question = msg[1]
    return "Poll updated!"


def reopen(args):
    """reopens a closed poll."""
    if not args.isadmin:
        return "Nope, not gonna do it."
    msg = args.msg.split()
    if not msg:
        return "Syntax: !poll reopen <pollnum>"
    if not msg[0].isdigit():
        return "Not a valid positve integer."
    pid = int(msg[0])
    poll = get_open_poll(args.session, pid)
    if poll is None:
        return "That poll doesn't exist or has been deleted!"
    poll.active = 1
    return "Poll %d reopened!" % pid


def end_poll(args):
    """Ends a poll."""
    if not args.isadmin:
        return "Nope, not gonna do it."
    if not args.msg:
        return "Syntax: !vote end <pollnum>"
    if not args.msg.isdigit():
        return "Not A Valid Positive Integer."
    poll = get_open_poll(args.session, int(args.msg))
    if poll is None:
        return "That poll doesn't exist or has already been deleted!"
    if poll.active == 0:
        return "Poll already ended!"
    poll.active = 0
    return "Poll ended!"


def tally_poll(args):
    """Shows the results of poll."""
    if not args.msg:
        return "Syntax: !vote tally <pollnum>"
    if not args.msg.isdigit():
        return "Not A Valid Positive Integer."
    pid = int(args.msg)
    poll = get_open_poll(args.session, pid)
    if poll is None:
        return "That poll doesn't exist or was deleted. Use !poll list to see valid polls"
    state = "Active" if poll.active == 1 else "Closed"
    votes = args.session.query(Poll_responses).filter(Poll_responses.pid == pid).all()
    args.send("%s poll: %s, %d total votes" % (state, poll.question, len(votes)))
    votemap = collections.defaultdict(list)
    for v in votes:
        votemap[v.response].append(v.voter)
    for x in sorted(votemap.keys()):
        args.send("%s: %d -- %s" % (x, len(votemap[x]), ", ".join(votemap[x])), target=args.nick)
    if not votemap:
        return ""
    ranking = collections.defaultdict(list)
    for x in votemap.keys():
        num = len(votemap[x])
        ranking[num].append(x)
    high = max(ranking)
    winners = (ranking[high], high)
    if len(winners[0]) == 1:
        winners = (winners[0][0], high)
        return "The winner is %s with %d votes." % winners
    else:
        winners = (", ".join(winners[0]), high)
        return "Tie between %s with %d votes." % winners


def get_response(session, pid, nick):
    return session.query(Poll_responses).filter(Poll_responses.pid == pid, Poll_responses.voter == nick).first()


def vote(session, nick, pid, response):
    """Votes on a poll."""
    if not response:
        return "You have to vote something!"
    if response == "n" or response == "nay":
        response = "no"
    elif response == "y" or response == "aye":
        response = "yes"
    poll = get_open_poll(session, pid)
    if poll is None:
        return "That poll doesn't exist or isn't active. Use !poll list to see valid polls"
    old_vote = get_response(session, pid, nick)
    if old_vote is None:
        session.add(Poll_responses(pid=pid, response=response, voter=nick))
        return "%s voted %s." % (nick, response)
    else:
        if response == old_vote.response:
            return "You've already voted %s." % response
        else:
            msg = "%s changed their vote from %s to %s." % (nick, old_vote.response, response)
            old_vote.response = response
            return msg


def retract(args):
    """Deletes a vote for a poll."""
    if not args.msg:
        return "Syntax: !vote retract <pollnum>"
    if not args.msg.isdigit():
        return "Not A Valid Positive Integer."
    response = get_response(args.session, args.msg, args.nick)
    if response is None:
        return "You haven't voted on that poll yet!"
    args.session.delete(response)
    return "Vote retracted"


def list_polls(args):
    num = args.session.query(Polls).filter(Polls.active == 1).count()
    return "There are %d polls. Check them out at %spolls.html" % (num, args.config['core']['url'])


@Command(['vote', 'poll'], ['db', 'nick', 'is_admin', 'type', 'config'])
def cmd(send, msg, args):
    """Handles voting.

    Syntax: {command} <start|end|list|tally|edit|delete|retract|reopen|(num) vote>

    """
    command = msg.split()
    msg = " ".join(command[1:])
    if not command:
        send("Which poll?")
        return
    else:
        command = command[0]
    # FIXME: integrate this with ArgParser
    if command.isdigit():
        if args['type'] == 'privmsg':
            send("We don't have secret ballots in this benevolent dictatorship!")
        else:
            send(vote(args['db'], args['nick'], int(command), msg))
        return
    isadmin = args['is_admin'](args['nick'])
    parser = arguments.ArgParser(args['config'])
    parser.set_defaults(session=args['db'], msg=msg, nick=args['nick'])
    subparser = parser.add_subparsers()
    start_parser = subparser.add_parser('start', config=args['config'], aliases=['open', 'add', 'create'])
    start_parser.set_defaults(func=start_poll, send=send, isadmin=isadmin, type=args['type'])
    tally_parser = subparser.add_parser('tally')
    tally_parser.set_defaults(func=tally_poll, send=send)
    list_parser = subparser.add_parser('list', config=args['config'])
    list_parser.set_defaults(func=list_polls)
    retract_parser = subparser.add_parser('retract')
    retract_parser.set_defaults(func=retract)
    end_parser = subparser.add_parser('end', aliases=['close'])
    end_parser.set_defaults(func=end_poll, isadmin=isadmin)
    delete_parser = subparser.add_parser('delete')
    delete_parser.set_defaults(func=delete_poll, isadmin=isadmin)
    edit_parser = subparser.add_parser('edit')
    edit_parser.set_defaults(func=edit_poll, isadmin=isadmin)
    reopen_parser = subparser.add_parser('reopen')
    reopen_parser.set_defaults(func=reopen, isadmin=isadmin)
    try:
        cmdargs = parser.parse_args(command)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    send(cmdargs.func(cmdargs))
