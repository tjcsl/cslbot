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
from requests import get

from ..helpers.command import Command


def get_incidents(key):
    req = get('https://api.wmata.com/Incidents.svc/json/Incidents', headers={'api_key': key})
    data = req.json()
    incidents = collections.defaultdict(list)
    for i in data['Incidents']:
        incidents[i['IncidentType']].append(i['Description'])
    return incidents


def get_type(t):
    t = t.capitalize()
    if t == 'Alert':
        return 'Alerts'
    if t == 'Delay':
        return 'Delays'
    return t


@Command(['metro', 'wmata'], ['config'])
def cmd(send, msg, args):
    """Provides Metro Info.

    Syntax: {command}

    """
    incidents = get_incidents(args['config']['api']['wmatakey'])
    if not incidents:
        send("No incidents found. Sure you picked the right metro system?")
        return
    for t, i in incidents.items():
        send("%s:" % get_type(t))
        for desc in i:
            send(desc)
