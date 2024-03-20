from typing import OrderedDict, Self
import datetime
from .base_entity import BaseEntity
from .network import Network
from ..smarter_client import SmarterClient


class User(BaseEntity):
    def __init__(self, client: SmarterClient):
        super().__init__(client)
        self.email = None
        self.accepted = None
        self.first_name = None
        self.last_name = None
        self.location_accepted = None
        self.networks_index = None
        self.temperature_unit = None

        self.networks = None

    def _init_data(self, data: OrderedDict) -> None:
        self.accepted: int = datetime.datetime.fromtimestamp(
            data.get('accepted')/1000.0)
        self.email: str = data.get('email')
        self.first_name: str = data.get('first_name')
        self.last_name: str = data.get('last_name')
        self.location_accepted: int = data.get('locationAccepted')
        self.networks_index = data.get('networks_index')
        self.temperature_unit: int = data.get('temperature_unit')

        self.networks = {value: Network.from_id(self.client,
                                                key) for key, value in self.networks_index}

    @staticmethod
    def _from_defaults(client: SmarterClient) -> Self:
        return User(client)

    def _fetch(self) -> OrderedDict:
        return self.client.get_user(self.identifier)
