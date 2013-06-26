import re
import subprocess


def cmd(send, msg, args):
        match = re.match('([A-Za-z0-9]+)', msg)
        if match:
            try:
                answer = subprocess.check_output(['wtf', match.group(1)],
                                                 stderr=subprocess.STDOUT)
                send(answer.decode().rstrip().replace('\n', ' or ').replace('fuck', 'fsck'))
            except subprocess.CalledProcessError as ex:
                send(ex.output.decode().rstrip())
