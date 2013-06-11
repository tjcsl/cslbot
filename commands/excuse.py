import subprocess
from config import CHANNEL


def cmd(e, c, msg):
        try:
            excuse = subprocess.check_output(['fortune', 'bofh-excuses'])
            c.privmsg(CHANNEL, excuse.decode().replace('\n', ' '))
        except subprocess.CalledProcessError:
            c.privmsg(CHANNEL, "BOFH Excuse #0: fortune-mod not installed, or bofh-excuses missing!")
