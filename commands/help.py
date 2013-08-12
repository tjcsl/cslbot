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

args = ['modules', 'nick', 'connection']
help_entry = {'!8ball':'<question>', '!about': '', '!acronym': '<word>',
              '!addquote': '<quote>','!admins': '', '!ahamilto': '',
              '!award': '<nickrname>', '!bc': '<math equation>', '!bike': '',
              '!blame': '<reason>','!bofh': '', '!bold': '<text>',
              '!botsnack': '<food>', '!channels': '', '!choose': '<arg1> or <arg2>',
              '!coin': '<number of coins (leave blank for one coin)>',
              '!creffett': '<message>', '!ddate': '', '!define': '<word>',
              '!demorse': '<morse code>', '!dialup': '', '!distro', '',
              '!ebay': '', '!eix': '<Gentoo command>', '!errno', '',
              '!excuse': '', '!fortune': '', '!fweather': '<location>',
              '!fwilson': '<message>', '!g': '<search query>', '!gcc': '',
              '!google': '<search query>', '!guarded': '<nickname>',
              '!help': '<command>', '!issue': '<issue>', '!isup': '<website>',
              '!kill': '<nickname>', '!listquotes': '', '!lmgtfy': '<search query>',
              '!meme': '', '!microwave': '<power> <person>', '!morse': '<text>',
              '!pester': '<nickname> <message>', '!pfoley': '<message>',
              '!ping': '<object>', '!praise': '<nickname>', '!pull': '',
              '!quit': '', '!quote': '', '!rage': '<message>', '!random': '',
              '!removequote': '<quote ID>', '!reverse': '<text>',
              '!s': '/<original text>/<new text>/<modifier>', '!say':'<message>',
              '!score': '<nickname>', '!sdamashek': '<message>',
              '!sha512': 'string', '!short': '<url>', '!slap': '<nickname>',
              '!slogan': '<message>', '!ssearch': '<message>', '!steam': '',
              '!throw': '<object>', '!time': '', '!urban': '<term>', '!version': '',
              '!weather': 'set[optional] <location>', '!wiki': '<article>',
              '!wikipath': '<article1> <article2>', '!word': '',
              '!wtf': '<acronym>', '!xkcd': '<number>', '!yoda': '<phrase>' }
              
              

def cmd(send, msg, args):
    if not msg:
        modules = sorted(args['modules'])
        num = int(len(modules) / 2)
        cmdlist1 = ' !'.join([x for x in modules[:num]])
        cmdlist2 = ' !'.join([x for x in modules[num:]])
        args['connection'].privmsg(args['nick'], 'Commands: !' + cmdlist1)
        args['connection'].privmsg(args['nick'], '!' + cmdlist2)
    else:
        if msg[0] != '!':
    	msg = '!' + msg
        args['connection'].privmsg(args['nick'], 'Syntax for ' + msg + ': ' + msg + ' '+ help_entry[msg])

