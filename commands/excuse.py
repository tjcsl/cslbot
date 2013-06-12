import subprocess


def cmd(send, msg, args):
        try:
            excuse = subprocess.check_output(['fortune', 'bofh-excuses'])
            send(excuse.decode().replace('\n', ' '))
        except subprocess.CalledProcessError:
            send("BOFH Excuse #0: fortune-mod not installed, or bofh-excuses missing!")
