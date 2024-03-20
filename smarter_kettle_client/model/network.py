from typing import OrderedDict, Self

from .device import Device
from .user import User

from .base_entity import BaseEntity

from ..smarter_client import SmarterClient


class Network(BaseEntity):
    def __init__(self, client: SmarterClient):
        super().__init__(client)
        self.access_tokens_fcm = None
        self.associated_devices = None
        self.name = None
        self.owner = None

    def _fetch(self) -> OrderedDict:
        return self.client.get_network(self.identifier)

    def _init_data(self, data: OrderedDict) -> None:
        self.access_tokens_fcm = data.get('access_tokens_fcm')
        self.associated_devices = [Device.from_id(self.client,
                                                  key) for key in data.get('associated_devices')]

        self.name = data.get('name')
        self.owner = User.from_id(self.client, data.get('owner'))

    @staticmethod
    def _from_defaults(client: SmarterClient) -> Self:
        return Network(client)
