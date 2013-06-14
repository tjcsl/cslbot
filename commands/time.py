import time


def cmd(send, msg, args):
        bold = '\x02'
        timeformat = bold + "Date: " + bold + "%d/%m/%Y" + bold + "   Time: " + bold + "%I:%M:%S"
        send(time.strftime(timeformat))
