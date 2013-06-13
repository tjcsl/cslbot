import time
bold = '\u0002'
def cmd(send, msg, args):
        time = time.localtime()
        send(bold + 'Date:' + bold + time[1] + '/' + time[2] + '/' + time[0] +
             bold + 'Time' + bold + time[3] + ':' + time[4] + ':' + time[5])
