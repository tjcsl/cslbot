from random import randrange
def cmd(send, msg, args):
        if not msg:
            return
        type = randrange(1, 5)
        if(type == 1):
                type = 'gold'
        elif(type == 2):
                type = 'silver'
        elif(type == 3):
                type = 'bronze'
        elif(type == 4):
                type = 'platinum'
        else:
                pass
        send(msg + ': I hereby award you this' + type + 'medal.')
