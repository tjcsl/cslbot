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


@Hook(['pubmsg', 'action'], ['config', 'db', 'nick'])
def handle(send, msg, args):
    """ Get titles for urls.

    | Generate a short url.
    | Get the page title.
    """

    # crazy regex to match urls
    regex = re.compile(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?....]))""")
    urls = [x[0] for x in regex.findall(msg)]
    for url in urls:
        title = get_title(url)
        short = get_short(url)
        last = args['db'].query(Urls).filter(Urls.url == url).order_by(Urls.time.desc()).first()
        if args['config']['feature'].getboolean('linkread'):
            #604800 is seconds in a week, it forgets old links after a week :)
            if last and (time.time() - last.time < 604800):
                lasttime = strftime('at %H:%M:%S on %Y-%m-%d', localtime(last.time))
                send("Url %s previously posted %s by %s -- %s" % (short, lasttime, last.nick, title))
            else:
                send('** %s - %s' % (title, short))
        args['db'].add(Urls(url=url, title=title, nick=args['nick'], time=time()))
