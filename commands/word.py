from urllib.request import urlopen


def cmd(send, msg, args):
        html = urlopen('http://randomword.setgetgo.com/get.php', timeout=1).read()
        # strip BOM
        send(html.decode()[1:].rstrip())
