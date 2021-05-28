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

from random import shuffle

from TwitterSearch import TwitterSearch, TwitterSearchOrder

from ..helpers import arguments
from ..helpers.command import Command

_API = None


def get_search_api(config):
    global _API
    if _API:
        return _API
    consumer_key = config['api']['twitterconsumerkey']
    consumer_secret = config['api']['twitterconsumersecret']
    access_token = config['api']['twitteraccesstoken']
    access_token_secret = config['api']['twitteraccesstokensecret']

    _API = TwitterSearch(consumer_key=consumer_key,
                         consumer_secret=consumer_secret,
                         access_token=access_token,
                         access_token_secret=access_token_secret)
    return _API


def tweet_url(user, tid):
    return 'https://twitter.com/{}/status/{}'.format(user, tid)


def tweet_text(obj):
    user = obj['user']['screen_name']
    text = obj['text'].replace('\n', ' ')
    return '@{}: {} ({})'.format(user, text, tweet_url(user, obj['id_str']))


@Command('twitter', ['config', 'nick'])
def cmd(send, msg, args):
    """
    Search the Twitter API.
    Syntax: {command} <query> <--user username> <--count 1>
    """
    if not msg:
        send('What do you think I am, a bird?')
        return

    parser = arguments.ArgParser(args['config'])
    parser.add_argument('query', nargs='*')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--user', dest='user', default=None)
    group.add_argument('--count', dest='count', type=int, default=1)
    group.add_argument('--random', action='store_true', default=False)

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return

    api = get_search_api(args['config'])

    query = TwitterSearchOrder()
    keywords = [' '.join(cmdargs.query)]
    if cmdargs.user:
        keywords += ['from:{}'.format(cmdargs.user)]
    query.set_keywords(keywords)
    query.set_language('en')
    query.set_result_type('recent')
    query.set_include_entities(False)
    query.set_count(cmdargs.count)

    results = list(api.search_tweets_iterable(query))
    if not results:
        send('No tweets here!')
        return

    if cmdargs.random:
        shuffle(results)

    max_chan_tweets = 5
    max_pm_tweets = 25
    if cmdargs.count > max_pm_tweets:
        send("That's too many tweets! The maximum allowed through PM is {}".format(max_pm_tweets))
        return

    if cmdargs.count > max_chan_tweets:
        send("That's a lot of tweets! The maximum allowed in a channel is {}".format(max_chan_tweets))

    for i in range(0, min(cmdargs.count, max_pm_tweets)):
        if cmdargs.count <= max_chan_tweets:
            send(tweet_text(results[i]))
        else:
            send(tweet_text(results[i]), target=args['nick'])
