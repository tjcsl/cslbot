# Copyright (C) 2013-2018 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Tris Wilson
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

import datetime
import json
import re
import socket
from importlib import resources

import geoip2
from requests import get

from .. import static
from ..helpers import arguments, exception
from ..helpers.command import Command
from ..helpers.geoip import get_zipcode
from ..helpers.orm import Weather_prefs


def get_default(nick, session, send, config, source):
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
                except OSError:
                    pass
            else:
                hostip = hostip.group()
            if hostip:
                hostip = re.sub('-', '.', hostip)
                with resources.path(static, config['db']['geoip']) as db_file:
                    location = get_zipcode(str(db_file), hostip)
                if location is not None:
                    send(f"No default location for {nick}, GeoIP guesses that your zip code is {location}.")
                    return location
        except (FileNotFoundError, geoip2.errors.AddressNotFoundError):
            pass
        # default to TJHSST
        send("No default location for %s and unable to guess a location, defaulting to TJ (22312)." % nick)
        return '22312'
    else:
        return location


def valid_location(location, apikey):
    data = get(f'http://api.wunderground.com/api/{apikey}/conditions/q/{location}.json').json()
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
        data = get(f'http://api.wunderground.com/api/{apikey}/conditions/q/{cmdargs.string[1:]}.json').json()
        if 'current_observation' in data:
            data = {
                'display_location': {
                    'full': cmdargs.string[1:]
                },
                'weather': 'Sunny',
                'temp_f': '94.8',
                'feelslike_f': '92.6',
                'relative_humidity': '60%',
                'pressure_in': '29.98',
                'wind_string': 'Calm'
            }
            forecastdata = {
                'conditions': 'Thunderstorms... Extreme Thunderstorms... Plague of Insects... The Rapture... Anti-Christ',
                'high': {
                    'fahrenheit': '3841'
                },
                'low': {
                    'fahrenheit': '-6666'
                }
            }
            alertdata = {'alerts': [{'description': 'Apocalypse', 'expires': 'at the end of days'}]}
        elif 'results' in data['response']:
            send("%d results found, please be more specific" % len(data['response']['results']))
            return False
        else:
            send("Invalid or Ambiguous Location")
            return False
    else:
        try:
            data = get(f'http://api.wunderground.com/api/{apikey}/conditions/q/{cmdargs.string}.json').json()
            forecastdata = get(f'http://api.wunderground.com/api/{apikey}/forecast/q/{cmdargs.string}.json').json()
            alertdata = get(f'http://api.wunderground.com/api/{apikey}/alerts/q/{cmdargs.string}.json').json()
        except json.JSONDecodeError as e:
            raise exception.CommandFailedException(e)
        if 'current_observation' in data:
            data = data['current_observation']
        elif 'results' in data['response']:
            results = data['response']['results']
            names = ['{}/{}'.format(x['state'], x['country']) for x in results]
            send("{} results found, please be more specific: {}".format(len(results), ', '.join(names)))
            return False
        else:
            send("Invalid or Ambiguous Location")
            return False
        if 'forecast' in forecastdata:
            forecastdata = forecastdata['forecast']['simpleforecast']['forecastday'][0]
        else:
            send("WARNING: unable to retrieve forecast.")
            forecastdata = None
    send("Current weather for %s:" % data['display_location']['full'])
    weather = '%s, ' % data['weather'] if data['weather'] else ''
    current = '{}Temp: {} (Feels like {}), Humidity: {}, Pressure: {}", Wind: {}'.format(weather, data['temp_f'], data['feelslike_f'],
                                                                                         data['relative_humidity'], data['pressure_in'],
                                                                                         data['wind_string'])
    send(current)
    if forecastdata is not None:
        forecast = '{}, High: {}, Low: {}'.format(forecastdata['conditions'], forecastdata['high']['fahrenheit'], forecastdata['low']['fahrenheit'])
        send("Forecast: %s" % forecast)
    alertlist = []
    for alert in alertdata.get('alerts', []):
        alertlist.append("{}, expires {}".format(alert['description'], alert['expires']))
    if alertlist:
        send("Weather Alerts: %s" % ', '.join(alertlist))
    return True


def get_forecast(cmdargs, send, apikey):
    forecastdata = get(f'http://api.wunderground.com/api/{apikey}/forecast10day/q/{cmdargs.string}.json').json()
    if 'forecast' in forecastdata:
        forecastdata = forecastdata['forecast']['simpleforecast']['forecastday']
    elif 'results' in forecastdata['response']:
        send("%d results found, please be more specific" % len(forecastdata['response']['results']))
        return False
    else:
        send("Invalid or Ambiguous Location")
        return False
    for day in forecastdata:
        if (day['date']['day'], day['date']['month'], day['date']['year']) == (cmdargs.date.day, cmdargs.date.month, cmdargs.date.year):
            forecast = '{}, High: {}, Low: {}'.format(day['conditions'], day['high']['fahrenheit'], day['low']['fahrenheit'])
            send("Forecast for {} on {}: {}".format(cmdargs.string, cmdargs.date.strftime("%x"), forecast))
            return
    send("Couldn't find data for %s in the 10-day forecast" % (cmdargs.date.strftime("%x")))


def get_hourly(cmdargs, send, apikey):
    forecastdata = get(f'http://api.wunderground.com/api/{apikey}/hourly10day/q/{cmdargs.string}.json').json()
    if 'hourly_forecast' in forecastdata:
        forecastdata = forecastdata['hourly_forecast']
    elif 'results' in forecastdata['response']:
        send("%d results found, please be more specific" % len(forecastdata['response']['results']))
        return False
    else:
        send("Invalid or Ambiguous Location")
        return False
    if not cmdargs.date:
        cmdargs.date = datetime.datetime.now()
    for hour in forecastdata:
        # wunderground's API returns strings rather than ints for the date for some reason, so casting is needed here
        date = (int(hour['FCTIME'][x]) for x in ['hour', 'mday', 'mon', 'year'])
        if date == (cmdargs.hour, cmdargs.date.day, cmdargs.date.month, cmdargs.date.year):
            forecast = '{}, Temperature: {}'.format(hour['condition'], hour['temp']['english'])
            send("Forecast for {} on {} at {}00: {}".format(cmdargs.string, cmdargs.date.strftime("%x"), cmdargs.hour, forecast))
            return
    send("Couldn't find data for {} hour {} in the 10-day hourly forecast".format(cmdargs.date.strftime("%x"), cmdargs.hour))


@Command(['weather', 'bjones'], ['nick', 'config', 'db', 'name', 'source'])
def cmd(send, msg, args):
    """Gets the weather.

    Syntax: {command} <[--date (date)] [--hour (hour)] (location)|--set (default)>
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
        cmdargs.string = get_default(nick, args['db'], send, args['config'], args['source'])
    if cmdargs.hour is not None:
        get_hourly(cmdargs, send, apikey)
    elif cmdargs.date:
        get_forecast(cmdargs, send, apikey)
    else:
        get_weather(cmdargs, send, apikey)
