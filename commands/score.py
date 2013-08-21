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

import re
import json
from random import choice

args = ['srcdir', 'config']


def cmd(send, msg, args):
    """Gets scores.
    Syntax: !score <--high|--low|nick>
    """
    try:
        scorefile = args['srcdir'] + '/data/score'
        data = json.load(open(scorefile))
        match = re.match('([a-zA-Z0-9]+)', msg)
        if match:
            name = match.group(1).lower()
            try:
                score = data[name]
                botnick = args['config']['core']['nick']
                if name == botnick.lower():
                    output = 'has %s points! :)' % score
                    send(output, 'action')
                else:
                    send("%s has %i points!" % (name, score))
            except:
                send("Nobody cares about " + name)
        else:
            match = re.match('--(.*)', msg)
            if match:
                sorted_data = sorted(data, key=data.get)
                if match.group(1) == 'high':
                    send('High Scores:')
                    for x in [-1, -2, -3]:
                        try:
                            name = sorted_data[x]
                            send("%s: %s" % (name, data[name]))
                        except IndexError:
                            pass
                if match.group(1) == 'low':
                    send('Low Scores:')
                    for x in range(0, 3):
                        try:
                            name = sorted_data[x]
                            send("%s: %s" % (name, data[name]))
                        except IndexError:
                            pass
            elif msg:
                send("Invalid nick")
            else:
                name = choice(list(data.keys()))
                send("%s has %i points!" % (name, data[name]))
    except OSError:
        send("Nobody cares about anything.")
