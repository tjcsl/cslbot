import subprocess


def cmd(send, msg, args):
        try:
            toSend = subprocess.check_output(['ddate']).decode().rstrip()
        except subprocess.CalledProcessError:
            toSend = 'Today is the day you install ddate!'
        send(toSend)
