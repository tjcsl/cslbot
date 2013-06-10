from config import CHANNEL
from urllib.request import urlopen
import json


def cmd(e, c, msg):
        # pfoley's api key -- do not abuse
        apikey = 'c685cf5a0aa40e4f'
        if not msg:
            # default to TJHSST
            msg = '22312'
        html = urlopen('http://api.wunderground.com/api/%s/conditions/q/%s.json'
                       % (apikey, msg)).read().decode()
        forecasthtml = urlopen('http://api.wunderground.com/api/%s/forecast/q/%s.json'
                               % (apikey, msg)).read().decode()
        data = json.loads(html)
        if 'current_observation' in data:
            data = data['current_observation']
        else:
            c.privmsg(CHANNEL, "Invalid or Ambiguous Location")
            return
        forecastdata = json.loads(forecasthtml)['forecast']['simpleforecast']['forecastday'][0]
        c.privmsg(CHANNEL, "%s: Current weather for %s"
                  % (e.source.nick, data['display_location']['full']))
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
        c.privmsg(CHANNEL, current)
        c.privmsg(CHANNEL, forecast)
