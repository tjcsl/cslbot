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

args = ['db', 'nick', 'is_admin', 'connection']


def start_poll(cursor, msg):
    """ Starts a poll """
    cursor.execute("INSERT INTO polls(question,active,rowid,deleted) VALUES(?,1,NULL,0)",
                   (msg,))
    return "Poll created!"


def delete_poll(cursor, poll):
    """ Deletes a poll """
    if not poll:
        return "Syntax: !poll delete <pollnum>"
    if not poll.isdigit():
        return "Not A Valid Positive Integer."
    qid = int(poll)
    query_result = cursor.execute("SELECT active,deleted FROM polls WHERE id=?", (qid,)).fetchone()
    if query_result[0] == 1:
        return "You can't delete an active poll!"
    cursor.execute("UPDATE polls SET deleted=1 WHERE id=?", (qid,))
    return "Poll deleted."


def edit_poll(cursor, msg):
    """ Edits a poll """
    cmd = msg.split()
    if len(cmd) < 2:
        return "Syntax: !vote edit <pollnum> <question>"
    if not cmd[0].isdigit():
        return "Not A Valid Positive Integer."
    qid = int(cmd[0])
    if cursor.execute("SELECT count(1) FROM polls WHERE id=? AND deleted=0", (qid,)).fetchone()[0] == 0:
        return "That poll was deleted or does not exist!"
    newq = " ".join(cmd[1:])
    cursor.execute("UPDATE polls SET question=? WHERE id=?", (newq, qid))
    return "Poll updated!"


def end_poll(cursor, poll):
    """ Ends a poll """
    if not poll:
        return "Syntax: !vote end <pollnum>"
    if not poll.isdigit():
        return "Not A Valid Positive Integer."
    qid = int(poll)
    if cursor.execute("SELECT count(1) FROM polls WHERE id=? AND deleted=0", (qid,)).fetchone()[0] == 0:
        return "That poll doesn't exist or has already been deleted!"
    cursor.execute("UPDATE polls SET active=0 WHERE id=?", (qid,))
    return "Poll ended!"


def tally_poll(cursor, poll, send, c, target):
    """Shows the results of poll """
    if not poll:
        send("Syntax: !vote tally <pollnum>")
        return
    if not poll.isdigit():
        send("Not A Valid Positive Integer.")
    qid = int(poll)
    query_result = cursor.execute("SELECT question,active FROM polls WHERE deleted=0 AND id=?", (qid,)).fetchone()
    if query_result is None:
        send("That poll doesn't exist or was deleted. Use !poll list to see valid polls")
        return
    question = query_result[0]
    status = "unknwon"
    if (query_result[1] == 1):
        status = "Active"
    else:
        status = "Closed"
    votes = cursor.execute("SELECT response,voter FROM poll_responses WHERE qid=?", (qid,)).fetchall()
    send("%s poll: %s, %d total votes" % (status, question, len(votes)))
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


def vote(cursor, nick, poll, vote):
    """ Votes on a poll"""
    qid = int(poll)
    if cursor.execute("SELECT count(1) FROM polls WHERE id=? AND active=1 AND deleted=0", (qid,)).fetchone()[0] == 0:
        return "That poll doesn't exist or isn't active. Use !poll list to see valid polls"
    old_vote = cursor.execute("SELECT response FROM poll_responses WHERE qid=? AND voter=?", (qid, nick)).fetchone()
    output = ""
    if old_vote is not None:
        if vote == old_vote[0]:
            return "You've already voted %s." % vote
        else:
            cursor.execute("UPDATE poll_responses SET response=? WHERE qid=? AND voter=?", (vote, qid, nick))
            output = "%s changed his/her vote from %s to %s." % (nick, old_vote[0], vote)
    else:
        cursor.execute("INSERT INTO poll_responses(qid, response, voter, rowid) VALUES(?,?,?,NULL)",
                       (qid, vote, nick))
    return output


def retract(cursor, poll, nick):
    """ Deletes a vote for a poll """
    if not poll:
        return "Syntax: !vote retract <pollnum>"
    if not poll.isdigit():
        return "Not A Valid Positive Integer."
    poll = int(poll)
    if cursor.execute("SELECT count(1) FROM poll_responses WHERE voter=? AND qid=?", (nick, poll))[0] == 0:
        return "You haven't voted on that poll yet!"
    cursor.execute("DELETE FROM poll_responses WHERE voter=? AND qid=?", (nick, poll))
    return "Vote retracted"


def list_polls(cursor, send, c, nick):
    """ Sends nick the list of polls in a PM"""
    active_polls = cursor.execute("SELECT id,question FROM polls WHERE deleted=0").fetchall()
    if not active_polls:
        send("No polls currently active.")
        return
    for poll in active_polls:
        c.privmsg(nick, "%d): %s" % (poll[0], poll[1]))
    send("Polls sent in a pm")


def cmd(send, msg, args):
    """Handles voting.
    Syntax: !vote <start|end|list|tally|edit|delete|vote|retract>
    """
    cursor = args['db']
    cmd = msg.split()
    msg = " ".join(cmd[1:])
    if not cmd:
        send("Which poll?")
    elif cmd[0] == 'start' or cmd[0] == 'open' or cmd[0] == 'add' or cmd[0] == 'create':
        send(start_poll(cursor, msg))
    elif cmd[0] == 'end' or cmd[0] == 'close':
        if args['is_admin'](args['nick']):
            send(end_poll(cursor, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd[0] == 'delete':
        if args['is_admin'](args['nick']):
            send(delete_poll(cursor, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd[0] == 'edit':
        if args['is_admin'](args['nick']):
            send(edit_poll(cursor, msg))
        else:
            send("Nope, not gonna do it.")
    elif cmd[0] == 'tally':
        tally_poll(cursor, msg, send, args['connection'], args['nick'])
    elif cmd[0] == 'list':
        list_polls(cursor, send, args['connection'], args['nick'])
    elif cmd[0] == 'retract':
        send(retract(cursor, msg, args['nick']))
    elif cmd[0].isdigit():
        send(vote(cursor, args['nick'], cmd[0], msg))
    else:
        send("Syntax: !vote <pollnum> <vote>")
