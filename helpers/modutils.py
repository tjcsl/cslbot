# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Fox Wilson, Peter Foley, Srijay Kasturi,
# Samuel Damashek, James Forcier, and Reed Koser
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

import sys
from os.path import basename
import importlib
from glob import glob

# FIXME: put this in a config file
GROUPS = {
    'hooks': {
        'core': ['caps', 'note', 'scores', 'url'],
        'optional': ['band', 'butt', 'understanding', 'xkcd', 'reddit'],
        'disabled': ['bob', 'clippy', 'ctf', 'stallman']},
    'commands': {
        'core': ['about', 'admins', 'cancel', 'channels', 'defersay', 'guarded',
                 'help', 'highlight', 'hooks', 'mission', 'mode', 'msg', 'nicks', 'note',
                 'pull', 'score', 'seen', 's', 'stats', 'threads', 'timeout', 'uptime', 'version', 'vote'],
        'useful': ['quote', 'ping', 'google', 'reddit', 'weather', 'slogan', 'issue',
                   'isup', 'time', 'translate', 'wiki', 'wolf', 'urban', 'babble', 'bc', 'define'],
        'optional': ['8ball', 'acronym', 'ahamilto', 'bike', 'blame', 'botsnack',
                     'choose', 'cidr', 'clippy', 'coin', 'creffett', 'cve', 'ddate' 'demorse', 'distro',
                     'dvorak', 'ebay', 'eix', 'errno', 'filter', 'fml', 'fortune', 'fweather', 'fwilson', 'gcc',
                     'imdb', 'inspect', 'insult', 'ipa', 'jargon', 'kill', 'lmgtfy', 'meme', 'microwave', 'morse', 'nuke', 'pester',
                     'pfoley', 'praise', 'random', 'roman', 'sha512', 'shibe', 'signal', 'skasturi', 'slap', 'ssearch', 'steam',
                     'stock', 'stopwatch', 'summon', 'throw', 'wai', 'wikipath', 'word', 'wtf', 'xkcd', 'yoda', 'laudiacay']}}


def group_enabled(groups, mod_type, name):
    if mod_type == 'helpers':
        return True
    for group_name, group in GROUPS[mod_type].items():
        if group_name == 'disabled':
            continue
        if name in group:
            return True
    return False


def get_enabled(groups, moddir, mod_type):
    mods = []
    for f in glob(moddir + '/*.py'):
        name = basename(f).split('.')[0]
        if group_enabled(groups, mod_type, name):
            mods.append(name)
    return mods


def scan_and_reimport(groups, folder, mod_type):
    """ Scans folder for hooks """
    for mod in get_enabled(groups, folder, mod_type):
        mod_name = mod_type + "." + mod
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
        else:
            importlib.import_module(mod_name)
