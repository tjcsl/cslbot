import time
bold = '\u0002'
def cmd(send, msg, args):
        ctime = time.localtime()
        send(bold + 'Date:' + bold + str(ctime[1]) + '/' + str(ctime[2]) + '/' + str(ctime[0])
             + bold + 'Time' + bold + str(ctime[3]) + ':' + str(ctime[4]) + ':' + str(ctime[5]))
