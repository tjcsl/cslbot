from config import CHANNEL
import subprocess


def cmd(e, c, msg):
        try:
            toSend = subprocess.check_output(['ddate']).decode().rstrip()
        except subprocess.CalledProcessError:
            toSend = 'Today is the day you install ddate!'
        c.privmsg(CHANNEL, toSend)
