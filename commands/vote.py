# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashe, James Forcier and Reed Koser
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

from helpers.command import Command


def start_poll(cursor, msg):
    """ Starts a poll """
    if not msg:
        return "Polls need a question."
    cursor.execute("INSERT INTO polls(question) VALUES(?)", (msg,))
    return "Poll #%d created!" % cursor.lastrowid


def delete_poll(cursor, poll):
    """ Deletes a poll """
    if not poll:
        return "Syntax: !poll delete <pollnum>"
    if not poll.isdigit():
        return "Not A Valid Positive Integer."
    pid = int(poll)
    query_result = cursor.execute("SELECT active,deleted FROM polls WHERE pid=?", (pid,)).fetchone()
    if query_result[0] == 1:
        return "You can't delete an active poll!"
    cursor.execute("UPDATE polls SET deleted=1 WHERE pid=?", (pid,))
    return "Poll deleted."


def edit_poll(cursor, msg):
    """ Edits a poll """
    cmd = msg.split()
    if len(cmd) < 2:
        return "Syntax: !vote edit <pollnum> <question>"
    if not cmd[0].isdigit():
        return "Not A Valid Positive Integer."
    pid = int(cmd[0])
    if cursor.execute("SELECT count(1) FROM polls WHERE pid=? AND deleted=0", (pid,)).fetchone()[0] == 0:
        return "That poll was deleted or does not exist!"
    newq = " ".join(cmd[1:])
    cursor.execute("UPDATE polls SET question=? WHERE pid=?", (newq, pid))
    return "Poll updated!"


def reopen(cursor, msg):
    """ reopens a closed poll."""
    cmd = msg.split()
    if not cmd:
        return "Syntax: !poll reopen <pollnum>"
    if not cmd[0].isdigit():
        return "Not a valid positve integer."
    pid = int(cmd[0])
    if cursor.execute("SELECT count(1) FROM polls WHERE pid=? AND deleted=0", (pid,)).fetchone()[0] == 0:
        return "That poll doesn't exist or has been deleted!"
    cursor.execute("UPDATE polls SET active=1 WHERE pid=?", (pid,))
    return "Poll %d reopened!" % pid


def end_poll(cursor, poll):
    """ Ends a poll """
    if not poll:
        return "Syntax: !vote end <pollnum>"
    if not poll.isdigit():
        return "Not A Valid Positive Integer."
    pid = int(poll)
    if cursor.execute("SELECT count(1) FROM polls WHERE pid=? AND deleted=0", (pid,)).fetchone()[0] == 0:
        return "That poll doesn't exist or has already been deleted!"
    cursor.execute("UPDATE polls SET active=0 WHERE pid=?", (pid,))
    return "Poll ended!"


def tally_poll(cursor, poll, send, c, target):
    """Shows the results of poll """
    if not poll:
        send("Syntax: !vote tally <pollnum>")
        return
    if not poll.isdigit():
        send("Not A Valid Positive Integer.")
    pid = int(poll)
    query_result = cursor.execute("SELECT question,active FROM polls WHERE deleted=0 AND pid=?", (pid,)).fetchone()
    if query_result is None:
        send("That poll doesn't exist or was deleted. Use !poll list to see valid polls")
        return
    question = query_result[0]
    state = "Active" if query_result['active'] == 1 else "Closed"
    votes = cursor.execute("SELECT response,voter FROM poll_responses WHERE pid=?", (pid,)).fetchall()
    send("%s poll: %s, %d total votes" % (state, question, len(votes)))
    votemap = {}
    for v in votes:
        vote = v[0]
        nick = v[1]
        if vote not in votemap:
            votemap[vote] = []
        votemap[vote].append(nick)
    for x in sorted(votemap.keys()):
        c.privmsg(target, "%s: %d -- %s" % (x, len(votemap[x]), ", ".join(votemap[x])))
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


def vote(cursor, nick, pid, vote):
    """ Votes on a poll"""
    if not vote:
        return "You have to vote something!"
    if vote == "0" or vote == "n" or vote == "nay":
        vote = "no"
    elif vote == "1" or vote == "y" or vote == "aye":
        vote = "yes"
    if cursor.execute("SELECT count(1) FROM polls WHERE pid=? AND active=1 AND deleted=0", (pid,)).fetchone()[0] == 0:
        return "That poll doesn't exist or isn't active. Use !poll list to see valid polls"
    old_vote = cursor.execute("SELECT response FROM poll_responses WHERE pid=? AND voter=?", (pid, nick)).fetchone()
    if old_vote is None:
        cursor.execute("INSERT INTO poll_responses(pid, response, voter) VALUES(?,?,?)", (pid, vote, nick))
        return "%s voted %s." % (nick, vote)
    else:
        if vote == old_vote['response']:
            return "You've already voted %s." % vote
        else:
            cursor.execute("UPDATE poll_responses SET response=? WHERE pid=? AND voter=?", (vote, pid, nick))
            return "%s changed his/her vote from %s to %s." % (nick, old_vote['response'], vote)


def retract(cursor, poll, nick):
    """ Deletes a vote for a poll """
    if not poll:
        return "Syntax: !vote retract <pollnum>"
    if not poll.isdigit():
        return "Not A Valid Positive Integer."
    poll = int(poll)
    if cursor.execute("SELECT count(1) FROM poll_responses WHERE voter=? AND pid=?", (nick, poll)).fetchone()[0] == 0:
        return "You haven't voted on that poll yet!"
    cursor.execute("DELETE FROM poll_responses WHERE voter=? AND pid=?", (nick, poll))
    return "Vote retracted"


def list_polls(cursor, c, nick):
    """ Sends nick the list of polls in a PM"""
    polls = cursor.execute("SELECT pid,question FROM polls WHERE deleted=0").fetchall()
    if not polls:
        return "No polls currently active."
    for poll in polls:
        c.privmsg(nick, "%d): %s" % (poll['pid'], poll['question']))
    return "%d currently active polls." % len(polls)


@Command(['vote', 'poll'], ['db', 'nick', 'is_admin', 'connection', 'type'])
def cmd(send, msg, args):
    """Handles voting.
    Syntax: !vote <start|end|list|tally|edit|delete|vote|retract>
    """
    cursor = args['db']
    cmd = msg.split()
    msg = " ".join(cmd[1:])
    if not cmd:
        send("Which poll?")
        return
    else:
        cmd = cmd[0]
    if cmd == 'start' or cmd == 'open' or cmd == 'add' or cmd == 'create':
        if args['type'] == 'privmsg':
            send("We don't have secret ballots in this benevolent dictatorship!")
        else:
            send(start_poll(cursor, msg))
    elif cmd == 'end' or cmd == 'close':
        if args['is_admin'](args['nick']):
            send(end_poll(cursor, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd == 'delete':
        if args['is_admin'](args['nick']):
            send(delete_poll(cursor, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd == 'edit':
        if args['is_admin'](args['nick']):
            send(edit_poll(cursor, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd == 'tally':
        tally_poll(cursor, msg, send, args['connection'], args['nick'])
    elif cmd == 'list':
        send(list_polls(cursor, args['connection'], args['nick']))
    elif cmd == 'retract':
        send(retract(cursor, msg, args['nick']))
    elif cmd == 'reopen':
        if args['is_admin'](args['nick']):
            send(reopen(cursor, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd.isdigit():
        if args['type'] == 'privmsg':
            send("We don't have secret ballots in this benevolent dictatorship!")
        else:
            send(vote(cursor, args['nick'], int(cmd), msg))
    else:
        send('Invalid Syntax.')
