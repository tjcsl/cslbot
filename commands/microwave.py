import re
import time
import sys
from config import CHANNEL, ADMINS

limit = 5


def do_nuke(nick, target, c):
    c.privmsg(CHANNEL, "Please Stand By, Nuking " + target)
    c.privmsg_many([nick, target], "        ____________________          ")
    c.privmsg_many([nick, target], "     :-'     ,   '; .,   )  '-:       ")
    c.privmsg_many([nick, target], "    /    (          /   /      \\      ")
    c.privmsg_many([nick, target], "   /  ;'  \\   , .  /        )   \\    ")
    c.privmsg_many([nick, target], "  (  ( .   ., ;        ;  '    ; )    ")
    c.privmsg_many([nick, target], "   \\    ,---:----------:---,    /    ")
    c.privmsg_many([nick, target], "    '--'     \\ \\     / /    '--'     ")
    c.privmsg_many([nick, target], "              \\ \\   / /              ")
    c.privmsg_many([nick, target], "               \\     /                ")
    c.privmsg_many([nick, target], "               |  .  |               ")
    c.privmsg_many([nick, target], "               |, '; |               ")
    c.privmsg_many([nick, target], "               |  ,. |               ")
    c.privmsg_many([nick, target], "               | ., ;|               ")
    c.privmsg_many([nick, target], "               |:; ; |               ")
    c.privmsg_many([nick, target], "      ________/;';,.',\\ ________     ")
    c.privmsg_many([nick, target], "     (  ;' . ;';,.;', ;  ';  ;  )    ")


def cmd(e, c, msg):
        nick = e.source.nick
        levels = {1: 'Whirr...',
                  2: 'Vrrm...',
                  3: 'Zzzzhhhh...',
                  4: 'SHFRRRRM...',
                  5: 'GEEEEZZSH...',
                  6: 'PLAAAAIIID...',
                  7: 'KKKRRRAAKKKAAKRAKKGGARGHGIZZZZ...',
                  8: 'Nuke',
                  9: 'nneeeaaaooowwwwww..... BOOOOOSH BLAM KABOOM',
                  10: 'ssh root@remote.tjhsst.edu rm -rf ~'+nick}
        if msg == '':
            c.privmsg(CHANNEL, 'What to microwave?')
            return
        match = re.match('(-?[0-9]*) (.*)', msg)
        if not match:
            c.privmsg(CHANNEL, 'Power level?')
        else:
            level = int(match.group(1))
            target = match.group(2)
            if level > 10:
                c.privmsg(CHANNEL, 'Aborting to prevent extinction of human race.')
                return
            if level < 1:
                c.privmsg(CHANNEL, 'Anti-matter not yet implemented.')
                return
            if level > 7 and nick not in ADMINS:
                c.privmsg(CHANNEL, "I'm sorry. Nukes are a admin-only feature")
                return
            for i in range(1, level+1):
                if i == 8:
                    do_nuke(nick, target, c)
                else:
                    c.privmsg(CHANNEL, levels[i])
                time.sleep(1)
            c.privmsg(CHANNEL, 'Ding, your %s is ready.' % target)
            if level == 10:
                time.sleep(5)
                c.quit("Caught in backwash.")
                sys.exit(0)
