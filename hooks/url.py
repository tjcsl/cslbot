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

from time import time, strftime, localtime
from helpers.urlutils import get_title, get_short
from helpers.orm import Urls
from helpers.hook import Hook
import re
import polr

@Hook(['pubmsg', 'action'], ['config', 'db', 'nick'])
def handle(send, msg, args):
    """ Get titles for urls.

    | Generate a short url.
    | Get the page title.
    """

    #FIXME: don't hardcode.
    if "http://git.io" in msg:
        return
    #FIXME: also, don't hardcode.
    if "polr" in msg and "http" in msg:
        return
    # crazy regex to match urls
    match = re.search(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.]
                          [a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()
                          <>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*
                          \)|[^\s`!()\[\]{};:'\".,<>?....]))""", msg)
    if match:
        url = match.group(1)
        title = get_title(url)
        short = get_short(url, polr.api(apikey =  args['config']['api']['polrkey']))
        last = args['db'].query(Urls).filter(Urls.url == url).order_by(Urls.time.desc()).first()
        if args['config']['feature'].getboolean('linkread'):
           # if last:
           #     lasttime = strftime('at %H:%M:%S on %Y-%m-%d', localtime(last.time))
           #     send("Url %s previously posted %s by %s -- %s" % (short, lasttime, last.nick, title))
           # else:
           send('** %s - %s' % (title, short))
        args['db'].add(Urls(url=url, title=title, nick=args['nick'], time=time()))
