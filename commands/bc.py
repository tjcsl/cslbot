import subprocess
import json
from os.path import dirname


def cmd(send, msg, args):
        if not msg:
            return
        data = json.load(open(dirname(__file__)+"/../score"))
        for u in data:
            msg = msg.replace(u, str(data[u]))
        msg += '\n'
        proc = subprocess.Popen(['bc', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.communicate(msg.encode())[0]
        output = output.decode().strip().replace('\n', ' ')
        send(output)
