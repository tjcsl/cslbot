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

from time import localtime, strftime
from helpers.hook import Hook


@Hook(['pubmsg', 'action'], ['nick', 'db'])
def handle(send, msg, args):
    cursor = args['db'].get()
    nick = args['nick']
    notes = cursor.execute('SELECT note,submitter,time,id FROM notes where nick=? ORDER BY time ASC', (nick,)).fetchall()
    for note in notes:
        time = strftime('at %H:%M:%S on %Y-%m-%d', localtime(note['time']))
        send("%s: A note from %s was left for you %s -- %s" % (nick, note['submitter'], time, note['note']))
        cursor.execute('DELETE FROM notes WHERE id=?', (note['id'],))
    cursor.commit()
