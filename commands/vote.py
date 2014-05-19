# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashe, James Forcier and Reed Koser
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

from helpers.orm import Polls, Poll_responses
from helpers.command import Command


def start_poll(session, msg, isadmin, send, nick, ctrlchan):
    """ Starts a poll """
    if not msg:
        send("Polls need a question.")
    poll = Polls(question=msg, submitter=nick)
    session.add(poll)
    session.flush()
    if isadmin:
        poll.accepted = 1
        send("Poll #%d created!" % poll.id)
    else:
        send("Poll submitted for approval.", target=nick)
        send("New Poll: #%d -- %s, Submitted by %s" % (poll.id, msg, nick), target=ctrlchan)


def delete_poll(session, pid):
    """ Deletes a poll """
    if not pid:
        return "Syntax: {command} <pollnum>"
    if not pid.isdigit():
        return "Not A Valid Positive Integer."
    poll = session.query(Polls).filter(Polls.accepted, Polls.id == pid).first()
    if poll is None:
        return "Poll does not exist."
    if poll.active == 1:
        return "You can't delete an active poll!"
    elif poll.deleted == 1:
        return "Poll already deleted."
    poll.deleted = 1
    return "Poll deleted."


def edit_poll(session, msg):
    """ Edits a poll """
    cmd = msg.split(maxsplit=1)
    if len(cmd) < 2:
        return "Syntax: {command} <question>"
    if not cmd[0].isdigit():
        return "Not A Valid Positive Integer."
    pid = int(cmd[0])
    poll = session.query(Polls).filter(Polls.deleted == 0, Polls.accepted == 1, Polls.id == pid).first()
    if poll is None:
        return "That poll was deleted or does not exist!"
    poll.question = cmd[1]
    return "Poll updated!"


def reopen(session, msg):
    """ reopens a closed poll."""
    cmd = msg.split()
    if not cmd:
        return "Syntax: {command} <pollnum>"
    if not cmd[0].isdigit():
        return "Not a valid positve integer."
    pid = int(cmd[0])
    poll = session.query(Polls).filter(Polls.deleted == 0, Polls.accepted == 1, Polls.id == pid).first()
    if poll is None:
        return "That poll doesn't exist or has been deleted!"
    poll.active = 1
    return "Poll %d reopened!" % pid


def end_poll(session, pid):
    """ Ends a poll """
    if not pid:
        return "Syntax: {command} <pollnum>"
    if not pid.isdigit():
        return "Not A Valid Positive Integer."
    poll = session.query(Polls).filter(Polls.deleted == 0, Polls.accepted == 1, Polls.id == pid).first()
    if poll is None:
        return "That poll doesn't exist or has already been deleted!"
    poll.active = 0
    return "Poll ended!"


def tally_poll(session, pid, send, target):
    """Shows the results of poll """
    if not pid:
        send("Syntax: {command} <pollnum>")
        return
    if not pid.isdigit():
        send("Not A Valid Positive Integer.")
        return
    poll = session.query(Polls).filter(Polls.deleted == 0, Polls.accepted == 1, Polls.id == pid).first()
    if poll is None:
        send("That poll doesn't exist or was deleted. Use !poll list to see valid polls")
        return
    state = "Active" if poll.active == 1 else "Closed"
    votes = session.query(Poll_responses).filter(Poll_responses.pid == pid).all()
    send("%s poll: %s, %d total votes" % (state, poll.question, len(votes)))
    votemap = {}
    for vote, nick in votes:
        if vote not in votemap:
            votemap[vote] = []
        votemap[vote].append(nick)
    for x in sorted(votemap.keys()):
        send("%s: %d -- %s" % (x, len(votemap[x]), ", ".join(votemap[x])), target=target)
    if not votemap:
        return
    ranking = {}
    for x in votemap.keys():
        num = len(votemap[x])
        if num not in ranking:
            ranking[num] = []
        ranking[num].append(x)
    high = max(ranking)
    winners = (ranking[high], high)
    if len(winners[0]) == 1:
        winners = (winners[0][0], high)
        send("The winner is %s with %d votes." % winners)
    else:
        winners = (", ".join(winners[0]), high)
        send("Tie between %s with %d votes." % winners)


def vote(session, nick, pid, vote):
    """ Votes on a poll"""
    if not vote:
        return "You have to vote something!"
    if vote == "n" or vote == "nay":
        vote = "no"
    elif vote == "y" or vote == "aye":
        vote = "yes"
    poll = session.query(Polls).filter(Polls.deleted == 0, Polls.accepted == 1, Polls.id == pid).first()
    if poll is None:
        return "That poll doesn't exist or isn't active. Use !poll list to see valid polls"
    old_vote = session.query(Poll_responses).filter(Poll_responses.pid == pid, Poll_responses.voter == nick).first()
    if old_vote is None:
        session.add(Poll_responses(pid=pid, response=vote, voter=nick))
        return "%s voted %s." % (nick, vote)
    else:
        if vote == old_vote.response:
            return "You've already voted %s." % vote
        else:
            msg = "%s changed his/her vote from %s to %s." % (nick, old_vote.response, vote)
            old_vote.response = vote
            return msg


def retract(session, pid, nick):
    """ Deletes a vote for a poll """
    if not pid:
        return "Syntax: {command} <pollnum>"
    if not pid.isdigit():
        return "Not A Valid Positive Integer."
    response = session.query(Poll_responses).filter(Poll_responses.pid == pid, Poll_responses.voter == nick).first()
    if response is None:
        return "You haven't voted on that poll yet!"
    session.delete(response)
    return "Vote retracted"


def list_polls(session, poll_url):
    num = session.query(Polls).count()
    return "There are %d polls. Check them out at %spolls.html" % (num, poll_url)


@Command(['vote', 'poll'], ['db', 'nick', 'is_admin', 'type', 'config'])
def cmd(send, msg, args):
    """Handles voting.
    Syntax: {command} <start|end|list|tally|edit|delete|vote|retract>
    """
    session = args['db']
    cmd = msg.split()
    msg = " ".join(cmd[1:])
    if not cmd:
        send("Which poll?")
        return
    else:
        cmd = cmd[0]
    isadmin = args['is_admin'](args['nick'])
    if cmd == 'start' or cmd == 'open' or cmd == 'add' or cmd == 'create':
        if args['type'] == 'privmsg':
            send("We don't have secret ballots in this benevolent dictatorship!")
        else:
            start_poll(session, msg, isadmin, send, args['nick'], args['config']['core']['ctrlchan'])
    elif cmd == 'tally':
        tally_poll(session, msg, send, args['nick'])
    elif cmd == 'list':
        send(list_polls(session, args['config']['core']['url']))
    elif cmd == 'retract':
        send(retract(session, msg, args['nick']))
    elif cmd.isdigit():
        if args['type'] == 'privmsg':
            send("We don't have secret ballots in this benevolent dictatorship!")
        else:
            send(vote(session, args['nick'], int(cmd), msg))
    elif cmd == 'end' or cmd == 'close':
        if isadmin:
            send(end_poll(session, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd == 'delete':
        if isadmin:
            send(delete_poll(session, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd == 'edit':
        if isadmin:
            send(edit_poll(session, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd == 'reopen':
        if isadmin:
            send(reopen(session, msg))
        else:
            send("Nope, not gonna do it.")
    else:
        send('Invalid Syntax.')
