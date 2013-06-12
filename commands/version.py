import subprocess
from urllib.request import urlopen
import json
import os


def cmd(send, msg, args):
        apiOutput = json.loads(urlopen('https://api.github.com/repos/fwilson42/ircbot/branches/master', timeout=1).read().decode())
        gitdir = os.path.dirname(__file__)+"/../.git"
        try:
            version = subprocess.check_output(['git', '--git-dir='+gitdir, 'show', '--format=oneline']).decode().split('\n')[0].split(' ')[0]
        except subprocess.CalledProcessError:
            send("Couldn't get the version.")
        if not msg:
            send(version)
        else:
            if msg == 'master':
                send(apiOutput['commit']['sha'])
            elif msg == 'check':
                check = 'Same' if apiOutput['commit']['sha'] == version else 'Different'
                send(check)
            else:
                send('Invalid argument')
