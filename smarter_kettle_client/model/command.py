from typing import OrderedDict

from ..smarter_client import SmarterClient


class Command:
    def __init__(self, client: SmarterClient, name: str, data: OrderedDict):
        self.client = client
        self.name = name
        self.example = data.get('example')
