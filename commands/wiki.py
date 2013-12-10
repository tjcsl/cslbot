# Copyright (C) 2013 Fox Wilson, Peter Foley, Srijay Kasturi, Samuel Damashek, James Forcier and Reed Koser
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
from helpers.urlutils import get_short
import re


def titlecase(s):  # copy-pasta'd from pydocs
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(), s)


def find_article(wiki_num, api_url, wiki_list, msg, names):
    data = get(api_url[wiki_num], params={'format': 'json', 'action': 'query', 'list': 'search', 'srlimit': '1', 'srsearch': msg}).json()
    try:
        return [False, data['query']['search'][0]['title']]
    except KeyError:
        return [True, msg[1]]  # so the wiki's api is screwed up, we'll re-check in a bit
    except IndexError:
        return [None, "%s isn't important enough to have a %s article." % (titlecase(msg[1]), names[wiki_num])]


def get_blurb(wiki_num, api_url, wiki_list, article):
    try:
        blurb_data = get('%s?action=query&prop=extracts&format=json&explaintext&exintro&titles=%s' % (api_url[wiki_num], article.replace(' ', '_'))).json()
        blurb = list(blurb_data['query']['pages'].values())[0]['extract']
        if len(blurb) == 0:
            blurb_data = get("%s?format=json&action=query&titles=%s&prop=revisions&rvprop=content" % (api_url[wiki_num], article)).json()
            try:
                blurb = str(list(blurb_data['query']['pages'].values())[0]['revisions'][0]["*"])  # this is how we check again if it exists
            except KeyError:
                blurb = "nothing"
        return str(blurb)
    except Exception:
        blurb_data = get("%s?format=json&action=query&titles=%s&prop=revisions&rvprop=content" % (api_url[wiki_num], article)).json()
        try:
            blurb = str(list(blurb_data['query']['pages'].values())[0]['revisions'][0]["*"])  # this is how we check again if it exists
            return blurb
        except KeyError:
            return "nothing"


@Command('wiki', ['config'])
def cmd(send, msg, args):
    """Returns the first wikipedia result for the argument.
    Syntax: !wiki <term>
    """
    if not msg:
        send("Need a article.")
        return
    #setting up values
    wiki_list = args['config']['wiki']['list'].split(", ")
    api_url = args['config']['wiki']['api'].split(", ")
    names = args['config']['wiki']['names'].split(", ")
    if not msg.split(" ")[0] in wiki_list:
        msg = args['config']['wiki']['default'] + " " + msg
    msg = msg.split(" ", maxsplit=1)
    wiki_num = wiki_list.index(msg[0])  # check if the article exits, or find the closest redirect.
    article = find_article(wiki_num, api_url, wiki_list, msg, names)
    state = article[0]
    if state == "none":
        send(str(article[1]))
        return
    else:
        article = article[1]  # okay it exists. now let's find out what's really in it
    blurb = get_blurb(wiki_num, api_url, wiki_list, article)
    if blurb == "nothing":
        send("%s isn't important enough to have a %s article." % (titlecase(msg[1]), names[wiki_num]))
        return
    if blurb.startswith("Coordinates"):  # fixes issues with articles with extra stuff (i.e. location)
        send(blurb)
        blurb = blurb.split("\n", maxsplit=1)
        send(str(blurb))
    try:
        blurb = blurb.split("'''", maxsplit=1)[1].replace("\n", " ").replace("'''", "")
    except IndexError:
        blurb = blurb.replace("\n", " ")
    if len(blurb) > 256:
        blurb = blurb[:253] + "..."
    send("Info on %s from %s: %s" % (titlecase(article), names[wiki_num], blurb))
    send(get_short(args['config']['wiki']['article_url'].split(", ")[wiki_num] + article.replace(" ", "_")))
