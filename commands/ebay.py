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

import json
from random import choice
from config import EBAYAPIKEY
from urllib.request import urlopen, Request


def get_categories():
    url = 'http://open.api.ebay.com/shopping'
    url += '?callname=GetCategoryInfo'
    url += '&CategoryID=-1'
    url += '&IncludeSelector=ChildCategories'
    req = Request(url)
    req.add_header('X-EBAY-API-RESPONSE-ENCODING', 'JSON')
    req.add_header('X-EBAY-API-VERSION', '733')
    req.add_header('X-EBAY-API-APP-ID', EBAYAPIKEY)
    data = json.loads(urlopen(req).read().decode())
    categories = [category['CategoryID'] for category in data['CategoryArray']['Category']]
    categories.remove('-1')
    return categories


def get_item(category):
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
    req.add_header('X-EBAY-SOA-SECURITY-APPNAME', EBAYAPIKEY)
    data = json.loads(urlopen(req).read().decode())
    item = data['findItemsAdvancedResponse'][0]['searchResult'][0]
    if int(item['@count']) == 0:
        return None
    else:
        item = choice(item['item'])
    return item['title'][0]+' -- http://www.ebay.com/itm/'+item['itemId'][0]


def cmd(send, msg, args):
    categories = get_categories()
    item = None
    while not item:
        item = get_item(choice(categories))
    send(item)
