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
from itertools import groupby

args = ['nick', 'srcdir', 'is_admin']


def start_poll(pollfile, polls, poll):
    if not poll:
        return "Polls need a question."
    poll = {'question': poll, 'active': True, 'votes': {}}
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
    votes = sorted(polls[poll]['votes'])
    send("%s poll: %s, %d votes" % (status, question, len(votes)))
    votemap = {}
    for key, group in groupby(votes, key=lambda x: votes[x]):
        votemap[key] = list(group)
    for x in votemap:
        send("%s: %d -- %s" % (x, len(votemap[x]), ", ".join(votemap[x])))


def vote(pollfile, polls, nick, poll, vote):
    if not vote:
        return "Syntax: !vote <pollnum> <vote>"
    if not poll.isdigit():
        return "Not A Number."
    poll = int(poll)
    if len(polls) <= poll:
        return "Invalid poll index."
    poll = polls[poll]
    if not poll['active']:
        return "Poll ended."
    positive = ['yes', 'y', '1', 'aye']
    negative = ['no', 'n', '0', 'nay']
    if vote.lower() in positive:
        vote = 'yes'
    if vote.lower() in negative:
        vote = 'no'
    output = "%s voted %s." % (nick, vote)
    if nick in poll['votes']:
        if vote == poll['votes'][nick]:
            return "You've already voted %s." % vote
        else:
            output = "%s changed his/her vote from %s to %s." % (nick, poll['votes'][nick], vote)
    poll['votes'][nick] = vote
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
    Syntax: !vote <start|end|list|tally|vote>
    """
    pollfile = args['srcdir'] + "/data/polls"
    if os.path.isfile(pollfile):
        polls = json.load(open(pollfile))
    else:
        polls = []
    cmd = msg.split()
    msg = " ".join(cmd[1:])
    if not cmd:
        send("Which poll?")
    elif cmd[0] == 'start':
        send(start_poll(pollfile, polls, msg))
    elif cmd[0] == 'end':
        if args['is_admin'](args['nick']):
            send(end_poll(pollfile, polls, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd[0] == 'tally':
        tally_poll(polls, msg, send)
    elif cmd[0] == 'list':
        list_polls(polls, send)
    elif cmd[0].isdigit():
        send(vote(pollfile, polls, args['nick'], cmd[0], msg))
    else:
        send("Syntax: !vote <pollnum> <vote>")
