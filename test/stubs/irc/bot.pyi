from typing import Any
from irc.client import SimpleIRCClient

class ServerSpec:
  def __init__(self, host: str, port: int, password: str) -> None: ...
class SingleServerIRCBot(SimpleIRCClient):
  def __init__(self, server_list: List[ServerSpec], nickname: str, realname: str, **connect_parms: Dict[str,Any]) -> None: ...
