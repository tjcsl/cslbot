import imp
import re
import time
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
from random import choice
import sys
import subprocess
import os
import json
import handler
def isadmin(nick):
    admins = [
    "wikipedia/Fox-Wilson",
    "pool-96-231-161-251.washdc.fios.verizon.net",
    "wikipedia/Vacation9",
    "botters/staff/adran"
    ]
    if str(nick, encoding='utf8').split("@")[1] in admins:
        return True
    return False
def getwtf(wtf):
    answer = subprocess.check_output(["wtf", wtf])
    return answer
def geteix(eix):
    answer = subprocess.check_output(["eix", "-c", eix])
    answer = str(answer, "ascii").split("\n")[0]
    return answer
class MyHandler(DefaultCommandHandler):
    def __init__(self, *args, **kwargs):
        DefaultCommandHandler.__init__(self, *args, **kwargs)
        self.ignored = []
    def ignore(self, nick):
        self.ignored.append(nick)
    def privmsg(self, nick, chan, msg):
        msg = msg.decode()
        if not isadmin(nick):
            for i in self.ignored:
                if i in str(nick):
                    print("Ignoring!")
                    return
        # !ignore
        match = re.match('\!ignore (.*)', msg)
        if match:
            if not isadmin(nick):
                return
            self.ignore(match.group(1))
            helpers.msg(self.client, chan,
            "Now igoring %s." % match.group(1))
        match = re.match('\!admin reload', msg)
        if match:
            if not isadmin(nick):
                return
            reload(handler)
            helpers.msg(self.client, chan, str(handler))
            return
        # !cignore
        match = re.match("\!cignore", msg)
        if match:
            if not isadmin(nick): return
            self.ignored = []
            helpers.msg(self.client, chan, "Ignore list cleared.")
            print(self.ignored)
            return
        # !quit
        match = re.match('\!quit', msg)
        if match:
            if isadmin(nick):
                sys.exit(0)
            else:
                helpers.msg(self.client, chan,
                "No.")
            return
        # !wtf
        match = re.match('\!wtf ([A-Za-z0-9]+)', msg)
        if match:
            wtf = match.group(1)
            helpers.msg(self.client, chan, 
            "%s" % (getwtf(wtf).decode().strip("\n")\
            .replace("\n", ", ")))
            return
        # !eix
        match = re.match('\!eix ([A-Za-z0-9][A-Za-z0-9\\-_/]*)', msg)
        if match:
            wtf = match.group(1)
            helpers.msg(self.client, chan, 
            "%s" % (geteix(wtf)))
            return

        # !throw
        match = re.match('\!throw (.*) at (.*)', msg)
        if match:
            helpers.msg(self.client, chan, "%s has been\
 thrown at %s!" % (match.group(1), match.group(2)))
            return
        # !kill
        match = re.match('\!kill (.*)', msg)
        if match:
            user = match.group(1)
            if user.lower() == "tjhsstbot":
                helpers.msg(self.client, chan,
                "I'm not that stupid!")
                return
            helpers.msg(self.client, chan, "Die, %s!" % user)
        # !say
        match = re.match('\!say (.*)', msg)
        if match:
            to_say = match.group(1).strip()
            print('Saying, "%s"' % to_say)
            helpers.msg(self.client, chan, to_say)
            return
        # !bike
        bicycle1 = " _f_,_"
        bicycle2 = "(_)`(_)"
        match = re.match("\!bike", msg)
        if match:
            helpers.msg(self.client, chan, bicycle1)
            helpers.msg(self.client, chan, bicycle2)
            return
        # !pester
        match = re.match("\!pester ([a-zA-Z0-9]+) (.*)", msg)
        if match:
            s = match.group(2)
            helpers.msg(self.client, chan, "%s: %s %s %s" % (match.group(1), s, s, s))
            return
        # !slogan
        match = re.match("\!slogan (.*)", msg)
        if match:
            thing = match.group(1).strip()
            choices = [
            "%s -- awesome.",
            "%s -- the future.",
            "The sight of %s.",
            "The wonder of %s!",
            "Amazing %s.",
            "%s is the best!",
            "%s: bug-free!"
            ]
            helpers.msg(self.client, chan, \
            choice(choices) % thing)
            return
        # !excuse
        match = re.match("\!excuse", msg)
        if match:
            x = choice(open("excuses", "r").readlines())
            helpers.msg(self.client, chan, x)
            return
        # ++ and --
        match = re.match(r"([a-zA-Z0-9]+)(\+\+|--)", msg)
        if match:
            uname = match.group(1)
            score = 1 if "+" in match.group(2) else -1
            scores = json.loads(open("score").read())
            if uname in scores:
                scores[uname] += score
            else:
                scores[uname] = score
            f = open("score", "w")
            f.write(json.dumps(scores))
            f.close()
            return
        # !score
        match = re.match("\!score ([a-zA-Z0-9]+)", msg)
        if match:
            uname = match.group(1)
            try: score = json.loads(open("score").read())[uname]
            except: score = 0
            finally: helpers.msg(self.client, chan, "%s has %i points!" % (uname, score))
            return
        match = re.match(r".*((?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))).*", msg)
        if match:
            print(match.group(1))
            import lxml.html
            t = lxml.html.parse(match.group(1))
            helpers.msg(self.client, chan, t.find(".//title").text)
            return
        # !award
        match = re.match("\!award (.*)", msg)
        if match:
            uname = match.group(1)
            helpers.msg(self.client, chan, "%s: I hereby award you this gold medal." % uname)
            return

        # !dialup
        match = re.match("\!dialup", msg)
        if match:
            helpers.msg(self.client, chan, "creffett: %s" % ("get dialup " * 15))

