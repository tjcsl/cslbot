def output_traceback(ex: Exception) -> Tuple[str, str]:
def handle_traceback(ex: Exception, c: client.ServerConnection, target: str, config: configparser.ConfigParser, source: str) -> None:
#        def send(_, msg: str) -> None:
