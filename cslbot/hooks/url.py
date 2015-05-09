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

import re
import time
import multiprocessing
from ..helpers import urlutils
from ..helpers.orm import Urls
from ..helpers.hook import Hook


def get_urls(msg):
    # crazy regex to match urls
    url_regex = re.compile(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?....]))""")
    return [x[0] for x in url_regex.findall(msg)]


@Hook('url', ['pubmsg', 'action'], ['config', 'db', 'nick', 'handler'])
def handle(send, msg, args):
    """ Get titles for urls.

    | Generate a short url.
    | Get the page title.
    """
    worker = args['handler'].workers
    result = worker.run_pool(get_urls, [msg])
    try:
        urls = result.get(5)
    except multiprocessing.TimeoutError:
        worker.restart_pool()
        send('Url regex timed out.')
        return
    for url in urls:
        # Prevent botloops
        if args['db'].query(Urls).filter(Urls.url == url, Urls.time > time.time() - 10).count() > 1:
            return
        title = urlutils.get_title(url)
        key = args['config']['api']['googleapikey']
        short = urlutils.get_short(url, key)
        last = args['db'].query(Urls).filter(Urls.url == url).order_by(Urls.time.desc()).first()
        if args['config']['feature'].getboolean('linkread'):
            if last is not None:
                lasttime = time.strftime('%H:%M:%S on %Y-%m-%d', time.localtime(last.time))
                send("Url %s previously posted at %s by %s -- %s" % (short, lasttime, last.nick, title))
            else:
                send('** %s - %s' % (title, short))
        args['db'].add(Urls(url=url, title=title, nick=args['nick'], time=time.time()))
