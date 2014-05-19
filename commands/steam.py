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

import pickle
from requests import get
from helpers.command import Command


def get_ids():
    steamidfile = open('steamids.pickle', 'rb')
    return pickle.load(steamidfile)


@Command('steam', ['config'])
def cmd(send, msg, args):
    """Gets steam status.
    Syntax: {command} <user>
    """
    apikey = args['config']['api']['steamapikey']
    if not apikey:
        send("API Key not specified.")
        return
    idlist = get_ids()
    try:
        params = {'key': apikey, 'steamids': idlist[msg]}
        output = get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/', params=params).json()
    except KeyError:
        send("I don't have that player in my database.")
        return
    try:
        output = output['response']['players'][0]
    except KeyError:
        send('Invalid Steam ID in database?')
        return
    send('Name: %s; Status: %s' % (output['personaname'], get_status(output)))


def get_status(vals):
    state = vals['personastate']
    if state == 0:
        return 'Offline'
    else:
        try:
            return 'In-game: ' + vals['gameextrainfo']
        except KeyError:
            return 'Online'
