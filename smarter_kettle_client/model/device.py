from typing import OrderedDict, Self


from smarter_kettle_client.model import Settings
from smarter_kettle_client.model import Command
from smarter_kettle_client.model import BaseEntity
from ..smarter_client import SmarterClient


class Device(BaseEntity):
    def __init__(self, client: SmarterClient):
        super().__init__(client)

        self.commands = None
        self.settings = None
        self.status = None

    def _init_data(self, data: OrderedDict):
        self.commands = {
            key: Command(self.client, key, value)
            for key, value in data.items()
        }

        self.settings = Settings(self.client, data.get('settings'))

        self.status = data.get('status')  # Status(client, data.get('status'))

    def _fetch(self) -> OrderedDict:
        return self.client.get_device(self.identifier)

    @staticmethod
    def _from_defaults(client: SmarterClient) -> Self:
        return Device(client)
