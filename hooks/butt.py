from helpers.hook import Hook


@Hook(types=['pubmsg'], args=['config'])
def handle(send, msg, args):
    done = False
    if "the cloud" in msg:
        msg = msg.replace("the cloud", "my butt")
        done = True
    if "cloud" in msg:
        msg = msg.replace("cloud", "butt")
        done = True
    if done:
        send(msg)
