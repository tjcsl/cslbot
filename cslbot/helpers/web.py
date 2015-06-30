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

import json
from simplejson import JSONDecodeError
from urllib.parse import unquote
from urllib.request import urlopen
from requests import post, get
from requests.exceptions import ReadTimeout
from requests_oauthlib import OAuth1Session
from . import urlutils


def get_rand_word():
    url = urlopen('http://www.urbandictionary.com/random.php').geturl()
    url = url.split('=')[1].replace('+', ' ')
    return unquote(url)


def get_urban(msg, key):
    if not msg:
        msg = get_rand_word()
        defn, url = get_urban_definition(msg, key)
        defn = "%s: %s" % (msg, defn)
    else:
        defn, url = get_urban_definition(msg, key)
    return defn, url


def get_urban_definition(msg, key):
    msg = msg.split()
    index = msg[0][1:] if msg[0].startswith('#') else None
    term = " ".join(msg[1:]) if index is not None else " ".join(msg)
    try:
        req = get('http://api.urbandictionary.com/v0/define', params={'term': term}, timeout=10)
        data = req.json()['list']
    except JSONDecodeError:
        return "UrbanDictionary is having problems.", None
    except ReadTimeout:
        return "UrbanDictionary timed out.", None
    if len(data) == 0:
        return "UrbanDictionary doesn't have an answer for you.", None
    elif index is None:
        output = data[0]['definition']
    elif not index.isdigit() or int(index) > len(data) or int(index) == 0:
        output = "Invalid Index"
    else:
        output = data[int(index) - 1]['definition']
    output = ' '.join(output.splitlines()).strip()
    if len(output) > 650:
        url = urlutils.get_short('http://urbandictionary.com/define.php?term=%s' % term, key)
    else:
        url = None
    return output, url


def create_issue(title, desc, nick, repo, apikey):
    body = {"title": title, "body": "%s\nIssue created by %s" % (desc, nick), "labels": ["bot"]}
    headers = {'Authorization': 'token %s' % apikey}
    req = post('https://api.github.com/repos/%s/issues' % repo, headers=headers, data=json.dumps(body))
    data = req.json()
    if 'html_url' in data.keys():
        return data['html_url'], True
    elif 'message' in data.keys():
        return data['message'], False
    else:
        return "Unknown error", False


def post_tumblr(config, blog, post):
    tumblr = OAuth1Session(
        client_key=config['api']['tumblrconsumerkey'],
        client_secret=config['api']['tumblrconsumersecret'],
        resource_owner_key=config['api']['tumblroauthkey'],
        resource_owner_secret=config['api']['tumblroauthsecret'])
    data = {'body': post}
    response = tumblr.post('https://api.tumblr.com/v2/blog/%s/post' % blog, params={'type': 'text'}, data=data).json()
    if response['meta']['status'] == 201:
        return "Posted!", True
    else:
        if isinstance(response['response'], dict):
            error = response['response']['errors'][0]
        else:
            error = response['meta']['msg']
    return "Got error %d from Tumblr: %s" % (response['meta']['status'], error), False
