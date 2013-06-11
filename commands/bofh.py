from config import CHANNEL
import hashlib
import subprocess

def cmd(e, c, msg):
        try:
            result = subprocess.check_output(['fortune',  'bofh-excuses'])
            toSend = result.decode().replace('\n', ' ')
        except:
            toSend = 'BOFH Excuse #-1:  fortune-mod not installed, or bofh-excuses missing!!'
        c.privmsg(CHANNEL, toSend)
