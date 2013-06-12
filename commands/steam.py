from config import CHANNEL, STEAMENABLE, STEAMAPIKEY
from steamids import idlist
from urllib.request import urlopen
import json


def cmd(e, c, msg):
        try:
            if STEAMENABLE:
                try:
                    output = urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' + STEAMAPIKEY + '&steamids=' + idlist[msg]).read().decode()
                except KeyError:
                    c.privmsg(CHANNEL, 'I don\'t have that player in my database.')
                    return
                except:
                    c.privmsg(CHANNEL, 'Error retrieving API data.')
                    return
                jsonOut = json.loads(output)
                try:
                    finalarr = jsonOut['response']['players'][0]
                except KeyError:
                    c.privmsg(CHANNEL, 'Invalid Steam ID in database?')
                    return
                c.privmsg(CHANNEL, 'Name: ' + finalarr['personaname'] + '; Status: ' + getStatus(finalarr))
        except:
            pass


def getStatus(vals):
        state = vals['personastate']
        if state == 0:
            return 'Offline'
        else:
            try:
                return 'In-game: ' + vals['gameextrainfo']
            except KeyError:
                return 'Online'
