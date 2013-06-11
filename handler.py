from config import ADMINS, CHANNEL
import re
import os
from glob import glob
import lxml.html
import urllib.request
import sys
import json
import importlib
import imp


class MyHandler():
    def __init__(self):
        self.ignored = []
        self.modules = self.loadmodules()
        self.abuselist = {}

    def loadmodules(self):
        modulemap = {}
        cmds = []
        for f in glob(os.path.dirname(__file__)+'/commands/*.py'):
            if os.access(f, os.X_OK):
                cmd = os.path.basename(f).split('.')[0]
                cmds.append(cmd)
        for cmd in cmds:
            modulemap[cmd] = importlib.import_module("commands."+cmd)
        return modulemap

    def pubmsg(self, c, e):
        nick = e.source.nick
        msg = e.arguments[0].strip()
        if nick not in ADMINS:
            for nick in self.ignored:
                print("Ignoring!")
                return
        # is this a command?
        cmd = msg.split()[0]
        args = msg[len(cmd)+1:]
        if cmd[0] == '!':
            if cmd[1:] in self.modules:
                mod = self.modules[cmd[1:]]
                try:
                    mod.cmd(e, c, args)
                except Exception as ex:
                    c.privmsg(CHANNEL, 'Exception: ' + str(ex))
                return

        #special commands
        if cmd[0] == '!':
            if cmd[1:] == 'help':
                cmdlist = self.modules.keys()
                cmdlist = ' !'.join([x for x in sorted(self.modules)])
                c.privmsg(CHANNEL, 'Commands: !' + cmdlist)
            # everything below this point requires admin
            if nick not in ADMINS:
                return
            if cmd[1:] == 'reload':
                c.privmsg(CHANNEL, "Aye Aye Capt'n")
                self.modules = self.loadmodules()
                for x in self.modules.values():
                    imp.reload(x)
                return
            elif cmd[1:] == 'quit':
                c.quit("Goodbye, Cruel World!")
                sys.exit(0)
                return
            elif cmd[1:] == 'cignore':
                self.ignored = []
                c.privmsg(CHANNEL, "Ignore list cleared.")
            elif cmd[1:] == 'ignore':
                if args in self.ignored:
                    return
                self.ignored.append(args)
                c.privmsg(CHANNEL,
                          "Now igoring %s." % args)
            elif cmd[1:] == 'join':
                c.join(args)
                c.privmsg(args, "Joined at the request of " + nick)

        # ++ and --
        match = re.search(r"([a-zA-Z0-9]+)(\+\+|--)", msg)
        if match:
            name = match.group(1)
            if "+" in match.group(2):
                score = 1
                if name == nick:
                    c.privmsg(CHANNEL, nick +
                              ": No self promotion! You lose 10 points.")
                    score = -10
            else:
                score = -1
            if os.path.isfile("score"):
                scores = json.load(open("score"))
            else:
                scores = {}
            if name in scores:
                scores[name] += score
            else:
                scores[name] = score
            f = open("score", "w")
            json.dump(scores, f)
            f.close()
            return

        # crazy regex to match urls
        match = re.match(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»....]))", msg)
        if match:
            t = lxml.html.parse(urllib.request.urlopen(match.group(1), timeout=1))
            c.privmsg(CHANNEL, t.find(".//title").text)
            return
