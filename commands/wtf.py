import re
import subprocess
from config import CHANNEL


def cmd(e, c, msg):
        match = re.match('([A-Za-z0-9]+)', msg)
        if match:
            try:
                answer = subprocess.check_output(['wtf', match.group(1)],
                                                 stderr=subprocess.STDOUT)
                c.privmsg(CHANNEL, answer.decode().rstrip())
            except subprocess.CalledProcessError as e:
                c.privmsg(CHANNEL, e.output.decode().rstrip())
