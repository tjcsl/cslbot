# -*- coding: utf-8 -*-
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

from requests.utils import quote
from TwitterSearch import TwitterSearch, TwitterSearchOrder, TwitterSearchException

from ..helpers.command import Command


def get_search_api(config):
    consumer_key = config['api']['twitterconsumerkey']
    consumer_secret = config['api']['twitterconsumersecret']
    access_token = config['api']['twitteraccesstoken']
    access_token_secret = config['api']['twitteraccesstokensecret']

    return TwitterSearch(consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret)


def tweet_url(user, tid):
    return 'https://twitter.com/{}/status/{}'.format(user, tid)


def tweet_text(obj):
    user = obj['user']['screen_name']
    return '@{}: {} ({})'.format(user, obj['text'], tweet_url(user, obj['id_str']))


@Command('twitter', ['config'])
def cmd(send, msg, args):
    """
    Search the Twitter API.
    Syntax: {command} <query> <--from username>
    """
    if not msg:
        send('What do you think I am, a bird?')
        return

    try:
        api = get_search_api(args['config'])
        query = TwitterSearchOrder()
        query.set_keywords([msg])
        query.set_language('en')
        query.set_include_entities(False)

        results = list(api.search_tweets_iterable(query))
        if not results:
            send('No tweets here!')
            return

        send(tweet_text(results[0]))
    except TwitterSearchException as e:
        send("Sorry, there's something wrong with the Twitter API")
        send('Twitter search exception: {}'.format(e), target=args['config']['core']['ctrlchan'])
