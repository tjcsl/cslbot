import subprocess
import re
from random import choice


def cmd(send, msg, args):
        errno = subprocess.check_output(['gcc', '-include', 'errno.h', '-fdirectives-only', '-E', '-xc', '/dev/null'])
        errors = re.findall('^#define (E[A-Z]*) ([0-9]+)', errno.decode(), re.MULTILINE)
        error = choice(errors)
        send('#define %s %s' % (error[0], error[1]))
