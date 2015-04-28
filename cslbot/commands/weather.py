# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
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

import geoip2
import datetime
import re
import socket
from os.path import join
from requests import get
from ..helpers import arguments
from ..helpers.orm import Weather_prefs
from ..helpers.command import Command
from ..helpers.geoip import get_zipcode
from pkg_resources import Requirement, resource_filename


def get_default(nick, session, handler, send, config, source):
    location = session.query(Weather_prefs.location).filter(Weather_prefs.nick == nick).scalar()
    if location is None:
        try:
            # attempt to get GeoIP location, can fail if the DB isn't available, hostmask doesn't have
            # an IP, etc.
            hostmask = source.split('@')[1]
            hostip = re.search(r"\d{1,3}[.-]\d{1,3}[.-]\d{1,3}[.-]\d{1,3}", hostmask)
            # If that failed, could be a v6 addr
            if not hostip:
                try:
                    socket.inet_pton(socket.AF_INET6, hostmask)
                    hostip = hostmask
                except socket.error:
                    pass
            else:
                hostip = hostip.group()
            if hostip:
                hostip = re.sub('-', '.', hostip)
                db_file = resource_filename(Requirement.parse('CslBot'), join('cslbot', config['db']['geoip']))
                location = get_zipcode(db_file, hostip)
                if location is not None:
                    send("No default location for %s, GeoIP guesses that your zip code is %s." % (nick, location))
                    return location
        except (FileNotFoundError, geoip2.errors.AddressNotFoundError):
            pass
        # default to TJHSST
        send("No default location for %s and unable to guess a location, defaulting to TJ (22312)." % nick)
        return '22312'
    else:
        return location


def valid_location(location, apikey):
    data = get('http://api.wunderground.com/api/%s/conditions/q/%s.json' % (apikey, location)).json()
    return 'current_observation' in data


def set_default(nick, location, session, send, apikey):
    """Sets nick's default location to location."""
    if valid_location(location, apikey):
        send("Setting default location")
        default = session.query(Weather_prefs).filter(Weather_prefs.nick == nick).first()
        if default is None:
            default = Weather_prefs(nick=nick, location=location)
            session.add(default)
        else:
            default.location = location
    else:
        send("Invalid or Ambiguous Location")


def get_weather(cmdargs, send, apikey):
    if cmdargs.string.startswith("-"):
        data = get('http://api.wunderground.com/api/%s/conditions/q/%s.json' % (apikey, cmdargs.string[1:])).json()
        if 'current_observation' not in data:
            send("Invalid or Ambiguous Location")
            return False
        data = {'display_location': {'full': cmdargs.string[1:]},
                'weather': 'Sunny', 'temp_f': '94.8', 'feelslike_f': '92.6', 'relative_humidity': '60%', 'pressure_in': '29.98', 'wind_string': 'Calm'}
        forecastdata = {'conditions': 'Thunderstorms... Extreme Thunderstorms... Plague of Insects... The Rapture... Anti-Christ',
                        'high': {'fahrenheit': '3841'}, 'low': {'fahrenheit': '-6666'}}
        alertdata = {'alerts': [{'description': 'Apocalypse', 'expires': 'at the end of days'}]}
    else:
        data = get('http://api.wunderground.com/api/%s/conditions/q/%s.json' % (apikey, cmdargs.string)).json()
        forecastdata = get('http://api.wunderground.com/api/%s/forecast/q/%s.json' % (apikey, cmdargs.string)).json()
        alertdata = get('http://api.wunderground.com/api/%s/alerts/q/%s.json' % (apikey, cmdargs.string)).json()
        if 'current_observation' in data:
            data = data['current_observation']
        else:
            send("Invalid or Ambiguous Location")
            return False
        forecastdata = forecastdata['forecast']['simpleforecast']['forecastday'][0]
    send("Current weather for %s:" % data['display_location']['full'])
    current = '%s, Temp: %s (Feels like %s), Humidity: %s, Pressure: %s", Wind: %s' % (
        data['weather'],
        data['temp_f'],
        data['feelslike_f'],
        data['relative_humidity'],
        data['pressure_in'],
        data['wind_string'])
    forecast = '%s, High: %s, Low: %s' % (
        forecastdata['conditions'],
        forecastdata['high']['fahrenheit'],
        forecastdata['low']['fahrenheit'])
    send(current)
    send("Forecast: " + forecast)
    if alertdata['alerts']:
        alertlist = []
        for alert in alertdata['alerts']:
            alertlist.append("%s, expires %s" % (
                alert['description'],
                alert['expires']))
        send("Weather Alerts: " + ', '.join(alertlist))
    return True


def get_forecast(cmdargs, send, apikey):
    forecastdata = get('http://api.wunderground.com/api/%s/forecast10day/q/%s.json' % (apikey, cmdargs.string)).json()
    if 'forecast' not in forecastdata:
        send("Invalid or Ambiguous Location")
        return False
    forecastdata = forecastdata['forecast']['simpleforecast']['forecastday']
    for day in forecastdata:
        if (day['date']['day'], day['date']['month'], day['date']['year']) == (cmdargs.date.day, cmdargs.date.month, cmdargs.date.year):
            forecast = '%s, High: %s, Low: %s' % (
                day['conditions'],
                day['high']['fahrenheit'],
                day['low']['fahrenheit'])
            send("Forecast for %s on %s: %s" % (cmdargs.string, cmdargs.date.strftime("%x"), forecast))
            return
    send("Couldn't find data for %s in the 10-day forecast" % (cmdargs.date.strftime("%x")))


def get_hourly(cmdargs, send, apikey):
    forecastdata = get('http://api.wunderground.com/api/%s/hourly10day/q/%s.json' % (apikey, cmdargs.string)).json()
    if 'hourly_forecast' not in forecastdata:
        send("Invalid or Ambiguous Location")
        return False
    if not cmdargs.date:
        cmdargs.date = datetime.datetime.now()
    forecastdata = forecastdata['hourly_forecast']
    for hour in forecastdata:
        # wunderground's API returns strings rather than ints for the date for some reason, so casting is needed here
        if (int(hour['FCTTIME']['hour']), int(hour['FCTTIME']['mday']), int(hour['FCTTIME']['mon']), int(hour['FCTTIME']['year'])) == (cmdargs.hour, cmdargs.date.day, cmdargs.date.month, cmdargs.date.year):
            forecast = '%s, Temperature: %s' % (
                hour['condition'],
                hour['temp']['english'])
            send("Forecast for %s on %s at %s00: %s" % (cmdargs.string, cmdargs.date.strftime("%x"), cmdargs.hour, forecast))
            return
    send("Couldn't find data for %s hour %s in the 10-day hourly forecast" % (cmdargs.date.strftime("%x"), cmdargs.hour))


@Command(['weather', 'bjones'], ['nick', 'config', 'db', 'name', 'source', 'handler'])
def cmd(send, msg, args):
    """Gets the weather.
    Syntax: {command} <[--date date] [--hour hour] location|--set default>
    Powered by Weather Underground, www.wunderground.com
    """
    apikey = args['config']['api']['weatherapikey']
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--date', action=arguments.DateParser)
    parser.add_argument('--hour', type=int)
    parser.add_argument('--set', action='store_true')
    parser.add_argument('string', nargs='*')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if isinstance(cmdargs.string, list):
        cmdargs.string = " ".join(cmdargs.string)
    if cmdargs.set:
        set_default(args['nick'], cmdargs.string, args['db'], send, apikey)
        return
    if cmdargs.hour is not None and cmdargs.hour > 23:
        send("Invalid Hour")
        cmdargs.hour = None
    nick = args['nick'] if args['name'] == 'weather' else '`bjones'
    if not cmdargs.string:
        cmdargs.string = get_default(nick, args['db'], args['handler'], send, args['config'], args['source'])
    if cmdargs.hour is not None:
        get_hourly(cmdargs, send, apikey)
    elif cmdargs.date:
        get_forecast(cmdargs, send, apikey)
    else:
        get_weather(cmdargs, send, apikey)
