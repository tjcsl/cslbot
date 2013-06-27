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

from urllib.request import urlopen
import json


def cmd(send, msg, args):
        # pfoley's api key -- do not abuse
        apikey = 'c685cf5a0aa40e4f'
        if not msg:
            # default to TJHSST
            msg = '22312'
        html = urlopen('http://api.wunderground.com/api/%s/conditions/q/%s.json'
                       % (apikey, msg), timeout=1).read().decode()
        forecasthtml = urlopen('http://api.wunderground.com/api/%s/forecast/q/%s.json'
                               % (apikey, msg), timeout=1).read().decode()
        data = json.loads(html)
        if 'current_observation' in data:
            data = data['current_observation']
        else:
            send("Invalid or Ambiguous Location")
            return
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
