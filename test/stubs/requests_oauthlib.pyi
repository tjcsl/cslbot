from requests import Session


class OAuth1Session(Session):

    def __init__(self, client_key: str, client_secret: str, resource_owner_key: str, resource_owner_secret: str) -> None:
        ...
