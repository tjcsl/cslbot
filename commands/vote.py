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

import json
import os

args = ['nick', 'srcdir', 'is_admin']


def start_poll(pollfile, polls, poll):
    if not poll:
        return "Polls need a question."
    poll = {'question': poll, 'active': True, 'for': [], 'against': []}
    polls.append(poll)
    save_polls(pollfile, polls)
    return "Poll created."


def end_poll(pollfile, polls, poll):
    if not poll:
        return "Syntax: !vote end <pollnum>"
    if not poll.isdigit():
        return "Not A Number."
    poll = int(poll)
    if len(polls) <= poll:
        return "Invalid poll index."
    polls[poll]['active'] = False
    save_polls(pollfile, polls)
    return "Poll ended."


def tally_poll(polls, poll, send):
    if not poll:
        send("Syntax: !vote tally <pollnum>")
        return
    if not poll.isdigit():
        send("Not A Number.")
        return
    poll = int(poll)
    if len(polls) <= poll:
        send("Invalid poll index.")
        return
    question = polls[poll]['question']
    status = "Active" if polls[poll]['active'] else "Ended"
    yes = polls[poll]['for']
    no = polls[poll]['against']
    send("%s poll: %s" % (status, question))
    if yes:
        send("For: %d -- %s" % (len(yes), " , ".join(yes)))
    else:
        send("For: 0")
    if no:
        send("Against: %d -- %s" % (len(no), " , ".join(no)))
    else:
        send("Against: 0")


def vote(pollfile, polls, nick, vote, poll):
    if not poll:
        return "Syntax: !vote <yes|no> <pollnum>"
    if not poll.isdigit():
        return "Not A Number."
    poll = int(poll)
    if len(polls) <= poll:
        return "Invalid poll index."
    poll = polls[poll]
    if not poll['active']:
        return "Poll ended."
    output = "%s voted %s." % (nick, vote)
    if vote == 'yes':
        if nick in poll['for']:
            return "You've already voted yes."
        elif nick in poll['against']:
            poll['against'].remove(nick)
            poll['for'].append(nick)
            output = "%s changed his/her vote from no to yes." % nick
        else:
            poll['for'].append(nick)
    else:
        if nick in poll['against']:
            return "You've already voted no."
        elif nick in poll['for']:
            poll['for'].remove(nick)
            poll['against'].append(nick)
            output = "%s changed his/her vote from yes to no." % nick
        else:
            poll['against'].append(nick)
    save_polls(pollfile, polls)
    return output


def list_polls(polls, send):
    if not polls:
        send("No polls.")
    else:
        for index, poll in enumerate(polls):
            send("%d: %s" % (index, poll['question']))


def save_polls(pollfile, polls):
    f = open(pollfile, "w")
    json.dump(polls, f, indent=True, sort_keys=True)
    f.write("\n")
    f.close()


def cmd(send, msg, args):
    """Handles voting.
    Syntax: !vote <start|end|list|tally|yes|no>
    """
    pollfile = args['srcdir'] + "/data/polls"
    if os.path.isfile(pollfile):
        polls = json.load(open(pollfile))
    else:
        polls = []
    positive = ['yes', 'y', '1', 'aye']
    negative = ['no', 'n', '0', 'nay']
    cmd = msg.split()
    msg = " ".join(cmd[1:])
    if not cmd:
        send("Missing argument.")
    elif cmd[0] == 'start':
        send(start_poll(pollfile, polls, msg))
    elif cmd[0] == 'end':
        if args['is_admin'](args['nick']):
            send(end_poll(pollfile, polls, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd[0] == 'tally':
        tally_poll(polls, msg, send)
    elif cmd[0] in positive:
        send(vote(pollfile, polls, args['nick'], 'yes', msg))
    elif cmd[0] in negative:
        send(vote(pollfile, polls, args['nick'], 'no', msg))
    elif cmd[0] == 'list':
        list_polls(polls, send)
    else:
        send("Invalid argument.")
