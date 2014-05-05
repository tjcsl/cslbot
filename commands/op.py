from helpers.command import Command


def mode(args, mode):
    args['handler'].connection.mode(args['target'], mode)

def op(args, msg):
    if not msg:
        mode(args, "+o %s" % args['nick'])
    else:
        mode(args, "+o %s" % msg)

def deop(args, msg):
    if not msg:
         mode(args, "-o %s" % args['nick'])
    else:
         mode(args, "-o %s" % msg)

def voice(args, msg):
    if not msg:
         mode(args, "+v %s" % args['nick'])
    else:
         mode(args, "+v %s" % msg)

def devoice(args, msg):
    if not msg:
         mode(args, "-v %s" % args['nick'])
    else:
         mode(args, "-v %s" % msg)

def kick(args, msg):
    if not msg:
       args['handler'].connection.kick(args['target'], args['nick'], args['nick'])
    else:
       args['handler'].connection.kick(args['target'], msg, msg)

def ban(args, msg):
    if not msg:
        mode(args, "+b %s!*@* %s!*@*" % (args['nick'], args['nick']))
    else:
        mode(args, "+bq %s %s" % (msg, msg))

@Command(['op', 'deop', 'voice', 'devoice', 'kick', 'kickban'], ['nick', 'is_admin', 'handler', 'botnick', 'target', 'name'])
def cmd(send, msg, args):
    """Ops, Deops, Voices, Devoices, Kicks, or Kickbans a user.
       Syntax: !command <nick>"""
    if args['target'] == 'private':
       send("Modes don't work in a PM!")
       return
    if not args['is_admin'](args['nick']):
       send("Admins only")
       return
    if args['botnick'] not in list(args['handler'].channels[args['target']].opers()):
       send("Bot must be opped")
       return
    name = args['name']
    if name == "op":
        op(args, msg)
    elif name == "deop":
        deop(args, msg)
    elif name == "voice":
        voice(args, msg)
    elif name == 'devoice':
        devoice(args, msg)
    elif name == 'kick':
        kick(args, msg)
    elif name == 'kickban':
        ban(args, msg)
        kick(args, msg)
