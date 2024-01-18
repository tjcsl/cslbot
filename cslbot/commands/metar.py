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

from xml.etree import ElementTree

from requests import get

from ..helpers import arguments
from ..helpers.command import Command


@Command(['metar'], ['nick', 'config', 'db', 'name', 'source', 'handler'])
def cmd(send, msg, args):
    """Gets the weather.

    Syntax: {command} <station> [station2...]

    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('stations', nargs='*')
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if not cmdargs.stations:
        send("What station?")
        return
    if isinstance(cmdargs.stations, list):
        cmdargs.stations = ','.join(cmdargs.stations)
    req = get('http://aviationweather.gov/adds/dataserver_current/httpparam',
              params={
                  'datasource': 'metars',
                  'requestType': 'retrieve',
                  'format': 'xml',
                  'mostRecentForEachStation': 'constraint',
                  'hoursBeforeNow': '1.25',
                  'stationString': cmdargs.stations
              })
    xml = ElementTree.fromstring(req.text)
    errors = xml.find('./errors')
    if len(errors):
        errstring = ','.join([error.text for error in errors])
        send('Error: %s' % errstring)
        return
    data = xml.find('./data')
    if data is None or data.attrib['num_results'] == '0':
        send('No results found.')
    else:
        for station in data:
            raw = station.find('raw_text')
            if raw:
                send(raw.text)
            else:
                send('No text found.')
