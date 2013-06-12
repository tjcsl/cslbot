from config import ADMINS, CHANNEL
import re
import os
from glob import glob
from random import random, choice
from lxml.html import parse
from urllib.request import urlopen, Request
from urllib.error import URLError
import json
import importlib
import imp
import time
import socket


class MyHandler():
    def __init__(self):
        self.ignored = []
        self.modules = self.loadmodules()
        self.abuselist = {}
        self.scorefile = os.path.dirname(__file__)+'/score'

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

    def ignore(self, send, nick):
        if nick not in self.ignored:
            self.ignored.append(nick)
            send("Now igoring %s." % nick)

    def abusecheck(self, send, nick, limit):
        if nick not in self.abuselist:
            self.abuselist[nick] = [time.time()]
        else:
            self.abuselist[nick].append(time.time())
        count = 0
        for x in self.abuselist[nick]:
            # 30 seconds - arbitrary cuttoff
            if (time.time() - x) < 30:
                count = count + 1
        if count > limit:
            self.send(CHANNEL, "%s is a Bot Abuser" % nick)
            self.ignore(send, nick)
            return False

    def privmsg(self, c, e):
        nick = e.source.nick
        msg = e.arguments[0].strip()
        if re.search(r"([a-zA-Z0-9]+)(\+\+|--)", msg):
            self.send(nick, 'Hey, no points in private messages!')
            return
        self.handle_msg('priv', c, e)

    def pubmsg(self, c, e):
        self.handle_msg('pub', c, e)

    #FIXME: remove this
    def send(self, target, msg):
        self.connection.privmsg(target, msg)

    def handle_msg(self, msgtype, c, e):
        nick = e.source.nick
        msg = e.arguments[0].strip()
        target = CHANNEL if msgtype == 'pub' else nick
        send = lambda msg: self.connection.privmsg(target, msg)
        if nick not in ADMINS and nick in self.ignored:
            send("Ignoring!" + nick)
            return
        # is this a command?
        cmd = msg.split()[0]
        cmdargs = msg[len(cmd)+1:]
        if cmd[0] == '!':
            if cmd[1:] in self.modules:
                mod = self.modules[cmd[1:]]
                args = {}
                if hasattr(mod, 'limit') and not self.abusecheck(send, nick, mod.limit):
                    return
                if hasattr(mod, 'args'):
                    for arg in mod.args:
                        if arg == 'channel':
                            args['channel'] = self.channel
                        else:
                            raise Exception("Invalid Argument: " + arg)
                mod.cmd(send, cmdargs, args)
                return

        #special commands
        if cmd[0] == '!':
            #FIXME: these should be split out
            if cmd[1:] == 'help':
                cmdlist = self.modules.keys()
                cmdlist = ' !'.join([x for x in sorted(self.modules)])
                send('Commands: !' + cmdlist)
            if cmd[1:] == 'blame':
                user = choice(self.channel.users())
                if args:
                    args = " for " + args
                send("I blame " + user + args)
            # everything below this point requires admin
            if nick in ADMINS:
                if cmd[1:] == 'reload':
                    send("Aye Aye Capt'n")
                    self.modules = self.loadmodules()
                    for x in self.modules.values():
                        imp.reload(x)
                    return
                elif cmd[1:] == 'cignore':
                    self.ignored = []
                    send("Ignore list cleared.")
                elif cmd[1:] == 'ignore':
                    self.ignore(send, args)
                #FIXME: CHANNEL is hardcoded in config.py
                elif cmd[1:] == 'join':
                    c.join(args)
                    self.send(args, "Joined at the request of " + nick)
                elif cmd[1:] == 'part':
                    self.send(args, "Leaving at the request of " + nick)
                    c.part(args)
        # ++ and --
        matches = re.findall(r"([a-zA-Z0-9]+)(\+\+|--)", msg)
        if matches:
            for match in matches:
                name = match[0].lower()
                if match[1] == "++":
                    score = 1
                    if name == nick.lower():
                        send(nick + ": No self promotion! You lose 10 points.")
                        score = -10
                else:
                    score = -1
                if os.path.isfile(self.scorefile):
                    scores = json.load(open(self.scorefile))
                else:
                    scores = {}
                if name in scores:
                    scores[name] += score
                else:
                    scores[name] = score
                f = open(self.scorefile, "w")
                json.dump(scores, f)
                f.write("\n")
                f.close()
            return

        # crazy regex to match urls
        match = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»....]))", msg)
        if match:
            try:
                url = match.group(1)
                if not url.startswith('http'):
                    url = 'http://' + url
                # Wikipedia doesn't like the default User-Agent
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                t = parse(urlopen(req, timeout=2))
                send('Website Title: ' + t.find(".//title").text.strip())
            except URLError as ex:
                # website does not exist
                if hasattr(ex.reason, 'errno') and ex.reason.errno == socket.EAI_NONAME:
                    return
                else:
                    send('%s: %s' % (type(ex), str(ex)))
            # page does not contain a title
            except AttributeError:
                pass
        if target == "#msbob" and random() < 0.25:
            self.modules['slogan'].cmd(e, c, {'args': 'MS BOB'})
