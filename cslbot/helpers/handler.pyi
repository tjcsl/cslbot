from typing import Any, Callable, Dict, List, Optional, Tuple
import configparser
from irc import client

send_type = Callable[..., None]


class BotHandler(object):

    def __init__(self, config: configparser.ConfigParser, connection: client.ServerConnection, channels: Dict[str, str], confdir: str) -> None:
        ...

    def do_args(self, modargs: List[str], send: send_type, nick: str, target: str, source: str, name: str, msgtype: str) -> Dict[str, Any]:
        ...

    def get_data(self):
        ...

    def set_data(self, data):
        ...

    def update_authstatus(self, nick):
        ...

    def send_who(self, target: str, tag: int) -> None:
        ...

    def is_admin(self, send: send_type, nick: str) -> bool:
        ...

    def get_admins(self):
        ...

    def abusecheck(self, send: send_type, nick: str, target: str, limit: int, cmd: str) -> bool:
        ...

    def send(self, target: str, nick: str, msg: str, msgtype: str, ignore_length=False, filters=None):
        ...

    def rate_limited_send(self, mtype: str, target: str, msg: Optional[str] = None) -> None:
        ...

    def do_log(self, target: str, nick: str, msg: str, msgtype: str) -> None:
        ...

    def do_part(self, cmdargs, nick, target, msgtype, send, c):
        ...

    def do_join(self, cmdargs, nick, msgtype, send, c):
        ...

    def check_mode(self, mode):
        ...

    def do_mode(self, target: str, msg: str, nick: str, send: send_type) -> None:
        ...

    def do_kick(self, send, target, nick, msg, slogan=True):
        ...

    def do_welcome(self):
        ...

    def is_ignored(self, nick: str) -> bool:
        ...

    def get_filtered_send(self, cmdargs: str, send: send_type, target: str) -> Tuple[str, send_type]:
        ...

    def handle_event(self, msg: str, send: send_type, c: client.ServerConnection, e: client.Event) -> None:
        ...

    def handle_authenticate(self, e):
        ...

    def handle_account(self, e):
        ...

    def handle_welcome(self):
        ...

    def handle_who(self, e):
        ...

    def handle_cap(self, e):
        ...

    def handle_nick(self, send, e):
        ...

    def handle_join(self, c: client.ServerConnection, e: client.Event, target: str, send: send_type) -> None:
        ...

    def get_cmd(self, msg: str) -> Tuple[str, str]:
        ...

    def run_cmd(self, send: send_type, nick: str, target: str, cmd_name: str, cmdargs: str, e: client.Event) -> None:
        ...

    def handle_kick(self, c: client.ServerConnection, e: client.Event, target: str, send: send_type) -> None:
        ...

    def handle_hooks(self, send: send_type, nick: str, target: str, e: client.Event, msg: str) -> None:
        ...

    def handle_msg(self, c: client.ServerConnection, e: client.Event) -> None:
        ...
