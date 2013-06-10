import re
import subprocess
from config import CHANNEL


def cmd(e, c, msg):
        match = re.match('([A-Za-z0-9][A-Za-z0-9\\-_/]*)', msg)
        if match:
                try:
                    answer = subprocess.check_output(['eix', '-c',
                                                     match.group(1)])
                    c.privmsg(CHANNEL, answer.decode().split('\n')[0].rstrip())
                except subprocess.CalledProcessError:
                    c.privmsg(CHANNEL, match.group(1)
                              + " isn't important enough for Gentoo.")
