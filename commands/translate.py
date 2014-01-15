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

import re
from requests import post, get
from helpers.command import Command


#FIXME: can cache for 10 minutes.
def get_token(client_id, secret):
    postdata = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': secret, 'scope': 'http://api.microsofttranslator.com'}
    data = post('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13', data=postdata).json()
    return data['access_token']


@Command(['translate', 'trans'], ['config'])
def cmd(send, msg, args):
    """Translate something.
    Syntax: !translate <text>
    """
    if not msg:
        send("Translate what?")
        return
    token = get_token(args['config']['api']['translateid'], args['config']['api']['translatesecret'])
    params = {'text': msg, 'to': 'en'}
    headers = {'Authorization': 'Bearer %s' % token}
    data = get('http://api.microsofttranslator.com/V2/Http.svc/Translate', params=params, headers=headers).text
    send(re.search('>(.*)<', data).group(1))
