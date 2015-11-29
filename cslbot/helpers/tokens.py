# -*- coding: utf-8 -*-
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import time
from requests import post


class Token():

    def __init__(self, update):
        self.time = 0
        self.key = 'invalid'
        self.update = update

    def __str__(self):
        return self.key


def update_translate_token(config, token):
    client_id, secret = config['api']['translateid'], config['api']['translatesecret']
    # Don't die if we didn't setup the translate api.
    if not client_id:
        token.key = 'invalid'
        return
    postdata = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': secret, 'scope': 'http://api.microsofttranslator.com'}
    data = post('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13', data=postdata).json()
    token.key = data['access_token']
    token.time = time.time()

token_cache = {'translate': Token(update_translate_token)}


def update_all_tokens(config):
    for token in token_cache.values():
        # The cache is valid for 10 minutes, refresh it only if it will expire in 1 minute or less.
        if time.time() - token.time > 9 * 60:
            token.update(config, token)
