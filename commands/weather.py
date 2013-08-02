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

import json
import re
from config import WEATHERAPIKEY
from urllib.request import urlopen
from urllib.parse import quote

args = ['nick', 'srcdir']


def get_default(nick, prefsfile, send):
    try:
        defaults = json.load(open(prefsfile))
        location = defaults[nick]
    except (OSError, KeyError):
        send("No default location for %s, defaulting to TJ." % nick)
        # default to TJHSST
        location = '22312'
    return location


def set_default(nick, location, prefsfile, send):
    try:
        defaults = json.load(open(prefsfile))
    except OSError:
        defaults = {}
    if get_weather(location, send):
        send("Setting default location")
        defaults[nick] = location
    f = open(prefsfile, "w")
    json.dump(defaults, f)
    f.write("\n")
    f.close()


def get_weather(msg, send):
    msg = quote(msg)
    if msg[0] == "-":
        html = urlopen('http://api.wunderground.com/api/%s/conditions/q/%s.json'
                   % (WEATHERAPIKEY, msg[1:]), timeout=1).read().decode()
        data = json.loads(html)
        if 'current_observation' not in data:
            send("Invalid or Ambiguous Location")
            return False
        data = {
            'display_location':{
                'full': msg[1:]              
                },
            'weather': 'Sunny',
            'temp_f': '94.8',
            'relative_humidity': '60%',
            'pressure_in': '29.98',
            'wind_string': 'Calm'
            }
        forecastdata = {
            'conditions': 'Thunderstorms... Extreme Thunderstorms... Plague of Insects... The Rapture... Anti-Christ',
            'high': {
                'fahrenheit': '-3841'
                },
            'low': {
                'fahrenheit': '-6666'
                }
        }
    else:
        html = urlopen('http://api.wunderground.com/api/%s/conditions/q/%s.json'
                   % (WEATHERAPIKEY, msg), timeout=1).read().decode()
        forecasthtml = urlopen('http://api.wunderground.com/api/%s/forecast/q/%s.json'
                           % (WEATHERAPIKEY, msg), timeout=1).read().decode()
        data = json.loads(html)
        if 'current_observation' in data:
            data = data['current_observation']
        else:
            send("Invalid or Ambiguous Location")
            return False
        forecastdata = json.loads(forecasthtml)['forecast']['simpleforecast']['forecastday'][0]
    send("Current weather for %s:" % data['display_location']['full'])
    current = '%s, Temp: %s, Humidity: %s, Pressure: %s", Wind: %s' % (
        data['weather'],
        data['temp_f'],
        data['relative_humidity'],
        data['pressure_in'],
        data['wind_string'])
    forecast = '%s, High: %s, Low: %s' % (
        forecastdata['conditions'],
        forecastdata['high']['fahrenheit'],
        forecastdata['low']['fahrenheit'])
    send(current)
    send("Forecast: " + forecast)
    return True


def cmd(send, msg, args):
    prefsfile = args['srcdir'] + "/data/weather"
    match = re.match("set (.*)", msg)
    if match:
        set_default(args['nick'], match.group(1), prefsfile, send)
        return
    if not msg:
        msg = get_default(args['nick'], prefsfile, send)
    get_weather(msg, send)
