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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import json
from random import choice
from urllib.request import Request, urlopen

from requests import get

from ..helpers.command import Command


def get_categories(apikey):
    params = {'callname': 'GetCategoryInfo', 'CategoryID': -1, 'IncludeSelector': 'ChildCategories'}
    headers = {'X-EBAY-API-RESPONSE-ENCODING': 'JSON', 'X-EBAY-API-VERSION': '733', 'X-EBAY-API-APP-ID': apikey}
    req = get('http://open.api.ebay.com/shopping', params=params, headers=headers)
    data = req.json()
    categories = [category['CategoryID'] for category in data['CategoryArray']['Category']]
    categories.remove('-1')
    return categories


# Only works with urllib's unencoded query strings.
def get_item(category, apikey):
    url = 'http://svcs.ebay.com/services/search/FindingService/v1'
    url += '?itemFilter(0).name=FreeShippingOnly&itemFilter(0).value=true'
    url += '&itemFilter(1).name=MaxPrice&itemFilter(1).value=1'
    url += '&itemFilter(1).paramName=Currency&itemFilter(1).paramValue=USD'
    url += '&itemFilter(2).name=ListingType'
    url += '&itemFilter(2).value(0)=StoreInventory&itemFilter(2).value(1)=FixedPrice&itemFilter(2).value(2)=AuctionWithBIN'
    url += '&categoryId=' + category
    req = Request(url)
    req.add_header('X-EBAY-SOA-RESPONSE-DATA-FORMAT', 'json')
    req.add_header('X-EBAY-SOA-OPERATION-NAME', 'findItemsAdvanced')
    req.add_header('X-EBAY-SOA-SECURITY-APPNAME', apikey)
    data = json.loads(urlopen(req).read().decode())
    item = data['findItemsAdvancedResponse'][0]['searchResult'][0]
    if int(item['@count']) == 0:
        return None
    else:
        item = choice(item['item'])
    return item['title'][0] + ' -- http://www.ebay.com/itm/' + item['itemId'][0]


@Command('ebay', ['config'])
def cmd(send, _, args):
    """Implements xkcd 576.
    Syntax: {command}
    """
    apikey = args['config']['api']['ebayapikey']
    categories = get_categories(apikey)
    item = None
    while not item:
        item = get_item(choice(categories), apikey)
    send(item)
