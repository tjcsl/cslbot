from config import CHANNEL
import subprocess

def cmd(e, c, msg):
        try:
            toSend = subprocess.check_output(['ddate']).decode().replace('\n', '')
        except:
            toSend = 'Today is the day you install ddate!'
        c.privmsg(CHANNEL, toSend)
