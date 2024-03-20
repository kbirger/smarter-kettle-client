from typing import OrderedDict
from ..smarter_client import SmarterClient


class Settings:
    def __init__(self, client: SmarterClient, data: OrderedDict):
        self.client = client
        self.network = data.get('network')
        self.network_ssid = data.get('network_ssid')
