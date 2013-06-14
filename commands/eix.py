import re
import subprocess


def cmd(send, msg, args):
        match = re.match('([A-Za-z0-9][A-Za-z0-9\\-_/]*)', msg)
        if match:
                try:
                    answer = subprocess.check_output(['eix', '-c',
                                                     match.group(1)])
                    send(answer.decode().split('\n')[0].rstrip())
                except subprocess.CalledProcessError:
                    send(match.group(1) + " isn't important enough for Gentoo.")
