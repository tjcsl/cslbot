from urllib.request import urlopen
from config import NICK


def cmd(send, msg, args):
    if (msg.startwith(NICK)):  # unimplemented
        response = urlopen("http://www.wdyl.com/profanity?q="+msg).read().decode('utf-8')  # returns a JSON response which contains 'True' if there is a swear word.
        if "True" in response:
            send("UW0TM8")
