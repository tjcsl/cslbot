import subprocess


def cmd(send, msg, args):
        if not msg:
            return
        msg += '\n'
        proc = subprocess.Popen(['bc', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.communicate(msg.encode())[0]
        output = output.decode().strip().replace('\n', ' ')
        send(output)
