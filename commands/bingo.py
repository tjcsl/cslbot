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

from random import choice
from helpers.command import Command

@Command('bingo', ['nick', 'connection'], limit=2)
def cmd(send, msg, args):
    spaces = ['"Still Alive" on piano', 'polo shirt', 'workstation broken', 'man man', 'csssuf on deadtom',
              '"oooh shiny"', 'cookie clicker', 'everyone is male', 'fwil-', 'someone hates java',
              'pit stains', 'jcotton\'s ipad', 'diet coke', 'booting itanium', 'ggolla has yogurt',
              'password change', 'jholtom uses music cart', 'khakis', 'zan mods mc', 'fwilson\'s stuff stolen',
              'zan feels inferior', 'FOOOOX', 'crashing the san', 'jholtom\'s plaid collared shirt', 'frozen pizza',
              'iodine breaks', 'mac in machine room', 'hipster web tech', 'ethanicorn', 'marching band',
              'ahamilto\'s laugh', '<creffett> zan--', 'xscreensaver bug', 'shibe', 'no shibing', '<skasturi> hi zan']

    board = [[None for i in range(5)] for j in range(5)]
    for i in range(5):
        for j in range(5):
            space = choice(spaces)
            board[i][j] = space
            spaces.remove(space)
    board[2][2] = 'free'

    lengths = [None for i in range(5)]
    for i in range(len(lengths)):
        lengths[i] = getLongestInColumn(board, i)

    for i in range(len(board)):
        for j in range(len(board[0])):
            while len(board[i][j]) < getLongestInColumn(board, j):
                board[i][j] += ' '

    c = args['connection']
    nick = args['nick']

    send('TJ SysLab Bingo', target=args['nick'])

    for i in range(len(board)):
        row = ""
        for j in range(len(board[0])):
            row += board[i][j] + " "
        send(row, target=args['nick'])

    send('------------------------------', target=args['nick'])
    send('Make yourself a real bingo board here: http://i.imgur.com/0Z3dxKw.png', target=args['nick'])


def getLongestInColumn(array, column):
    max = 0
    for i in range(1, len(array)):
        if len(array[i][column]) > len(array[max][column]):
            max = i
    return len(array[max][column])
