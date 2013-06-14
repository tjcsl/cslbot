import subprocess


def cmd(send, msg, args):
        if not msg:
            return
        msg += '\n'
        proc = subprocess.Popen(['bc', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.communicate(msg.encode())[0]
        send(output.decode().strip())
