from config import STEAMENABLE, STEAMAPIKEY
from steamids import idlist
from urllib.request import urlopen
import json


def cmd(send, msg, args):
    if STEAMENABLE:
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
