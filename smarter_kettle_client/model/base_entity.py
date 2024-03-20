from abc import ABCMeta
from abc import abstractmethod
from typing import OrderedDict, Self
from ..smarter_client import SmarterClient


class BaseEntity(metaclass=ABCMeta):
    def __init__(self, client: SmarterClient):
        self.identifier: str = None
        self.client = client
        self.is_stub = True

    @abstractmethod
    def _fetch(self) -> OrderedDict:
        pass

    @abstractmethod
    def _init_data(self, data: OrderedDict) -> None:
        pass

    def fetch(self):
        if self.is_stub:
            data = self._fetch()
            self._init_data(data)
            self.is_stub = False

    @staticmethod
    @abstractmethod
    def _from_defaults(client: SmarterClient) -> Self:
        pass

    @classmethod
    def from_id(cls, client: SmarterClient, identifier: str) -> Self:
        self = cls._from_defaults(client)
        self.client = client
        self.is_stub = True
        self.identifier = identifier

        return self

    @classmethod
    def from_data(cls, client: SmarterClient, data: OrderedDict) -> Self:
        self = cls(client)
        self._init_data(data)

        return self
