# Copyright (C) 2013-2014 Chaoyi Zha (cydrobolt), creators of cslbot
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

from requests import get
from helpers.command import Command


@Command(['polr','config'])
def cmd(send, msg, args):
    """Shortens a long URL using Polr - make sure to include http:// before a url.
    """
    apikey = ['config']['polr']['polrkey']
    tree = etree.parse("http://polr.cf/api" % args['config']['api']['polrkey'])
    send(tree.xpath('//text')[0].text)
