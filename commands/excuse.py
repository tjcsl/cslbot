import subprocess
from config import CHANNEL


def cmd(e, c, msg):
        excuse = subprocess.check_output(['fortune', 'bofh-excuses'])
        c.privmsg(CHANNEL, excuse.decode().split('\n')[-2].rstrip())
