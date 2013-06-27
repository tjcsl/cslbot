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

from config import STEAMENABLE, STEAMAPIKEY
from urllib.request import urlopen
import json
import pickle


def get_ids():
    steamidfile = open('steamids.pickle', 'rb')
    return pickle.load(steamidfile)


def cmd(send, msg, args):
        if STEAMENABLE:
            idlist = get_ids()
            try:
                output = urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' + STEAMAPIKEY + '&steamids=' + idlist[msg]).read().decode()
            except KeyError:
                send("I don't have that player in my database.")
                return
            except:
                send('Error retrieving API data.')
                return
            jsonOut = json.loads(output)
            try:
                finalarr = jsonOut['response']['players'][0]
            except KeyError:
                send('Invalid Steam ID in database?')
                return
            send('Name: ' + finalarr['personaname'] + '; Status: ' + getStatus(finalarr))


def getStatus(vals):
        state = vals['personastate']
        if state == 0:
            return 'Offline'
        else:
            try:
                return 'In-game: ' + vals['gameextrainfo']
            except KeyError:
                return 'Online'
