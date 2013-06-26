import pickle


def cmd(send, msg, args):
        try:
            picklefile = open('steamids.pickle', 'rb')
            idfile = pickle.load(picklefile)
        except:
            send('Error opening id file!')
            return
        for i in idfile.keys():
            match = i.lower().find(msg)
            if match != -1:
                i2 = i.encode('ascii', 'ignore').decode()
                send(i2)
