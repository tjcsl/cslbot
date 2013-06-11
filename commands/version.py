import subprocess
from config import CHANNEL
from urllib.request import urlopen
import json

def cmd(e, c, msg):
        apiOutput = json.loads(urlopen('https://api.github.com/repos/fwilson42/ircbot/branches/master', timeout=1).read().decode())
        try:
            version = subprocess.check_output(['git', 'show', '--format=oneline']).decode().split('\n')[0].split(' ')[0]
        except subprocess.CalledProcessError:
            c.privmsg(CHANNEL, "Couldn't get the version.")
        if msg != '':
            if msg == 'master':
                c.privmsg(CHANNEL, apiOutput['commit']['sha'])
            elif msg == 'check':
                same = 'Same' if apiOutput['commit']['sha'] == version else 'Different'
                c.privmsg(CHANNEL, same)
        else:
            c.privmsg(CHANNEL, version)
