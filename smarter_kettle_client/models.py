from __future__ import annotations
from . import smarter_client
from abc import ABCMeta
from abc import abstractmethod
from typing import OrderedDict, Self
import datetime
from pprint import pprint

# from smarter_kettle_client.smarter_client import SmarterClient


class BaseEntity(metaclass=ABCMeta):
    def __init__(self, client: smarter_client.SmarterClient):
        self.identifier: str = None
        self.client = client
        self.is_stub = True
        self._children: list[BaseEntity] = []

    def matches(self, path: list[str]) -> bool:
        return path[0] == self.entity_pathname() and path[1] == self.identifier

    def on_event(self, event):
        event_name: str = event.get('event')
        path: str = event.get('path')
        data: dict = event.get('data')
        path_list = [
            '/'] if path == '/' else path.strip('/').split('/') + ['/']

        if event_name != 'put' and event_name != 'patch':
            print(f'Unexpected event: {event_name}')
            pprint(event)
            return

        try:
            print(path, data)
            self.handle_update(event_name, path_list, data)
        except BaseException as e:
            print(f'Error handling update: {e}')
            pprint((event_name, path, data))

    def handle_update(self, event_name: str, path: list[str], data: dict):
        # pprint(('handle_update:', type(self).__name__, event_name, path))
        if path == ['/']:
            handler = None
            match event_name:
                case 'put':
                    handler = self.put
                case 'patch':
                    handler = self.patch

            handler(path, data)
        else:
            matched_children = list(filter(
                lambda child: child.matches(path), self._children))

            # print(('matched', list(map(lambda x: x.identifier, matched_children))))
            if not any(matched_children):
                if event_name == 'put':
                    self._children.append(
                        self.create_child(path[1:], data))
            else:
                for matched in matched_children:

                    matched.handle_update(event_name, path[1:], data)

    # def on_put(self, path: list[str], data: dict) -> None:
    #     pass

    # def on_patch(self, path: list[str], data: dict) -> None:
    #     pass

    def create_child(self, path: list[str], data: dict):
        raise NotImplementedError()

    @abstractmethod
    def entity_pathname(self) -> str:
        raise NotImplementedError()

    # @abstractmethod
    def put(self, path: list[str], data: dict) -> None:
        # print(f'{self} put {'/'.join(path)}')
        # if path[0] != self.entity_pathname():
        #     raise Exception(f'Unexpected path: {
        #                     '/'.join(path)} sent to {self}')

        if len(path) == 1:
            self._init_data(data)

    @abstractmethod
    def patch(self, path: list[str], data: dict) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _fetch(self) -> dict:
        pass

    @abstractmethod
    def _init_data(self, data: dict) -> None:
        pass

    def fetch(self):
        if self.is_stub:
            data = self._fetch()
            self._init_data(data)
            self.is_stub = False

    def __str__(self):
        return f'{self.__class__.__name__}({self.identifier})'

    @staticmethod
    @abstractmethod
    def _from_defaults(client: smarter_client.SmarterClient) -> Self:
        pass

    @classmethod
    def from_id(cls, client: smarter_client.SmarterClient, identifier: str) -> Self:
        self = cls._from_defaults(client)
        self.client = client
        self.is_stub = True
        self.identifier = identifier

        return self

    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict) -> Self:
        self = cls(client)
        self._init_data(data)

        return self


class Commands(BaseEntity, dict[str, 'Command']):
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)
        self.device: Device = None

    def _init_data(self, data: dict) -> None:

        # update the internal dict
        super().clear()
        self._build_commands(data)

        # track our children
        # todo: children should be a function
        self._children = list(self.values())

    def _build_commands(self, items: dict):
        super().update({
            key: Command.from_data(self.client, value, key, self)
            for key, value
            in items.items()
        })

    def _fetch(self) -> dict:
        raise NotImplementedError()

    @staticmethod
    def _from_defaults(client) -> Self:
        return Commands(client)

    def entity_pathname(self) -> str:
        'commands'

    def put(self, path: list[str], data: dict) -> None:
        self._init_data(data)

    def patch(self, path: list[str], data: dict) -> None:
        self._build_commands(data)

    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict, device: Device) -> Self:
        self = super().from_data(client, data)
        self.device = device

        return self


class CommandInstance(BaseEntity):
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)
        self.command = None
        self.device = None
        self.value = None
        self.state = None
        self.response = None
        self.user_id = None

    def _init_data(self, data: dict) -> None:
        self.user_id = data.get('user_id')
        self.value = data.get('value')
        self.state = data.get('state')
        self.response = data.get('response')

    def _fetch(self) -> dict:
        raise NotImplementedError()

    @staticmethod
    def _from_defaults(client) -> Self:
        return CommandInstance(client)

    def entity_pathname(self) -> str:
        return self.command.name

    # def put(self, path: list[str], data: dict) -> None:
    #     self._init_data(data, self.command, self.device)

    def handle_update(self, event_name: str, path: list[str], data: dict):

        if event_name != 'patch':
            print(self.value)
            raise RuntimeError(
                'CommandInstance cannot handle event other than patch')

        self.patch(path, data)

    def patch(self, path: list[str], data: dict) -> None:
        if data.get('state'):
            self.state = data.get('state')

        if data.get('response'):
            self.response = data.get('response')

        if data.get('value'):
            self.value = data.get('value')

        if data.get('user_id'):
            self.user_id = data.get('user_id')

    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict, identifier: str, command: Command, device: 'Device') -> Self:
        self = super().from_data(client, data)
        self.identifier = identifier
        self.command = command
        self.device = device

        return self


class Command(BaseEntity):
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)

        self.name: str = None
        self.device: Device = None
        self.instances: list[CommandInstance] = []

    def execute(self, user_id: str, value: any):
        return self.client.send_command(self.device.identifier, self.name, {"user_id": user_id, "value": value})

    def entity_pathname(self) -> str:
        return 'commands'

    def _init_data(self, data: dict) -> None:
        self.identifier = data.get('name')
        self.name = self.identifier
        self.example = data.get('example')

    def _fetch(self) -> dict:
        raise NotImplementedError()

    def create_child(self, path: list[str], data: dict):
        child = CommandInstance.from_data(
            self.client, data, path[0], self, self.device)
        self.instances.append(child)
        return child

    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict, name: str, device: Device) -> Self:
        self = super().from_data(client, data)
        self.identifier = name
        self.name = name
        self.device = device

        return self

    # def put(self, path: list[str], data: dict) -> None:
    #     print(f'Command{self.name} put {'/'.join(path)}')

    def patch(self, path: list[str], data: dict) -> None:
        print(f'Command{self.name} patch {'/'.join(path)}')

    @staticmethod
    def _from_defaults(client: smarter_client.SmarterClient) -> Self:
        return Command(client)


class Device(BaseEntity):
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)

        self.commands: Commands = None
        self.settings: Settings = None
        self.status: Status = None

    def _init_data(self, data: dict):
        self.commands = Commands.from_data(
            self.client, data.get('commands'), self)

        self.settings = Settings.from_data(self.client, data.get('settings'))

        # Status(client: smarter_client.SmarterClient, data.get('status'))
        self.status = Status.from_data(self.client, data.get('status'))

        self._children = [self.status, self.settings] + \
            list(self.commands.values())

    def _build_commands(self, data: dict):
        # create copy of the data dict with an additional key
        return {
            key: Command.from_data(self.client, value, key, self)
            for key, value
            in data.items()
        }

    def _fetch(self) -> dict:
        return self.client.get_device(self.identifier)

    def entity_pathname(self) -> str:
        'devices'

    # def put(self, path: list[str], data: dict) -> None:
    #     super().put(path, data)

    def patch(self, path: list[str], data: dict) -> None:
        super().patch(path, data)

    def watch(self, callback):
        def on_data(event):
            self.on_event(event)
            callback(event)
        self.client.watch_device_attribute(self.identifier, on_data)

    @staticmethod
    def _from_defaults(client) -> Self:
        return Device(client)


class LoginSession:
    def __init__(self, data: dict):
        self.kind = data.get('kind')
        self.local_id = data.get('localId')
        self.email = data.get('email')
        self.display_name = data.get('displayName')
        self.id_token = data.get('idToken')
        self.registered = data.get('registered')
        self.refresh_token = data.get('refreshToken')
        self.expires_in = data.get('expiresIn')

        self.expires_at = datetime.datetime.now() + datetime.timedelta(0,
                                                                       int(self.expires_in))

    def is_expired(self) -> bool:
        return self.expires_at > datetime.datetime.now()


class Network(BaseEntity):
    def __init__(self, client):
        super().__init__(client)
        self.access_tokens_fcm = None
        self.associated_devices = None
        self.name = None
        self.owner = None

    def _fetch(self) -> dict:
        return self.client.get_network(self.identifier)

    def _init_data(self, data: dict) -> None:
        self.access_tokens_fcm = data.get('access_tokens_fcm')
        self.associated_devices = [Device.from_id(self.client,
                                                  key) for key in data.get('associated_devices')]

        self.name = data.get('name')
        self.owner = User.from_id(self.client, data.get('owner'))

    @staticmethod
    def _from_defaults(client) -> Self:
        return Network(client)

    def entity_pathname(self) -> str:
        return 'networks'

    # def put(self, path: list[str], data: dict) -> None:
    #     super().put(path, data)

    def patch(self, path: list[str], data: dict) -> None:
        super().patch(path, data)


class Settings(BaseEntity):
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)
        self.identifier = '/'
        self.network: Network = None
        self.network_ssid: str = None

    def _fetch(self) -> dict:
        return dict()

    def _init_data(self, data: dict) -> None:
        self.network = Network.from_id(self.client, data.get('network'))
        self.network_ssid = data.get('network_ssid')

    @staticmethod
    def _from_defaults(client) -> Self:
        return Settings(client)

    def entity_pathname(self) -> str:
        return 'settings'

    # def put(self, path: list[str], data: dict) -> None:
    #     super().put(path, data)

    def patch(self, path: list[str], data: dict) -> None:
        super().patch(path, data)


class Status(BaseEntity, dict):
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)
        self.identifier = '/'

    def entity_pathname(self) -> str:
        return 'status'

    # def put(self, path: list[str], data: dict) -> None:
    #     self._init_data(data)

    def patch(self, path: list[str], data: dict) -> None:
        self.update(data)

    @staticmethod
    def _from_defaults(client: smarter_client.SmarterClient) -> Self:
        return Status(client)

    def _init_data(self, data: dict) -> None:
        self.clear()
        self.update(data)

    def _fetch(self) -> dict:
        self.client.get_status(self.identifier)


class User(BaseEntity):
    def __init__(self, client):
        super().__init__(client)
        self.email = None
        self.accepted = None
        self.first_name = None
        self.last_name = None
        self.location_accepted = None
        self.networks_index = None
        self.temperature_unit = None

        self.networks = None

    def _init_data(self, data: dict) -> None:
        self.accepted: int = datetime.datetime.fromtimestamp(
            data.get('accepted')/1000.0)
        self.email: str = data.get('email')
        self.first_name: str = data.get('first_name')
        self.last_name: str = data.get('last_name')
        self.location_accepted: int = data.get('locationAccepted')
        self.networks_index: dict = data.get('networks_index')
        self.temperature_unit: int = data.get('temperature_unit')

        self.networks = {value: Network.from_id(self.client,
                                                key) for key, value in self.networks_index.items()}

    @staticmethod
    def _from_defaults(client) -> Self:
        return User(client)

    def _fetch(self) -> dict:
        return self.client.get_user(self.identifier)

    def entity_pathname(self) -> str:
        return 'users'

    # def put(self, path: list[str], data: dict) -> None:
    #     super().put(path, data)

    def patch(self, path: list[str], data: dict) -> None:
        super().patch(path, data)
