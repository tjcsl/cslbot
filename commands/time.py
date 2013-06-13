import time
bold = '\u0002'
def cmd(send, msg, args):
        ctime = time.localtime()
        send(bold + 'Date:' + bold + ctime[1] + '/' + ctime[2] + '/' + ctime[0]
             + bold + 'Time' + bold + ctime[3] + ':' + ctime[4] + ':' + ctime[5])
