import datetime
from typing import Type
from unittest.mock import MagicMock, Mock
from zoneinfo import ZoneInfo

import pytest
import time_machine

from smarter_client.domain.models import (Command, CommandInstance, Commands,
                                          Device, LoginSession)
from smarter_client.domain.smarter_client import SmarterClient


@pytest.fixture
def SmarterClientMock(mocker):

    mock = MagicMock(
        name='SmarterClient',
        spec={
            'sign_in': Mock(),
            'refresh': Mock(),
            'get_user': Mock(),
            'get_network': Mock(),
            'get_device': Mock(),
            'get_status': Mock(),
            'send_command': Mock(),
            'watch_device_attribute': Mock(),

        }
    )
    return mock


class TestCommands:
    # def from_data_creates_instance(self):
    #     commands: Commands = Commands.from_data(
    #         {'test': {'test-instance': {'value': {'state': 'RCV'}}}})

    #     assert commands.get('test') == isinstance(Command)
    pass

    def test_from_data(self, mocker, SmarterClientMock):
        client = SmarterClientMock()

        assert isinstance(
            Commands.from_data(
                client,
                {'test': {'test-instance': {'value': {'state': 'RCV'}}}},
                mocker.MagicMock()
            ),
            Commands
        )

    def test_commands(self, mocker, SmarterClientMock):
        mock_client = SmarterClientMock()
        mock_device = mocker.MagicMock()

        command_from_data_spy = mocker.spy(Command, 'from_data')
        commands = Commands.from_data(mock_client,
                                      {'test': {
                                          'test-instance': {'value': {'state': 'RCV'}}}},
                                      mock_device
                                      )

        assert isinstance(commands.get('test'), Command)
        command_from_data_spy.assert_called_with(mock_client, {
            'test-instance': {'value': {'state': 'RCV'}}}, 'test', mock_device)

    def test_cannot_be_instantiated_from_id(self, mocker, SmarterClientMock):
        with pytest.raises(RuntimeError):
            Commands.from_id()


class TestCommandInstance:
    def test_from_data(self, mocker, SmarterClientMock):
        mock_client = SmarterClientMock()
        mock_device = mocker.MagicMock()
        mock_command = mocker.MagicMock()
        command = CommandInstance.from_data(
            mock_client,
            {
                'user_id': 'test',
                'value': 1,
                'state': 'RCV',
                'response': 1
            },
            'test',
            mock_command,
            mock_device
        )

        assert command.identifier == 'test'
        assert command.device == mock_device
        assert command.state == 'RCV'


class TestCommand:
    def test_command_from_data_should_create_instance(self, mocker, SmarterClientMock):
        mock_client = SmarterClientMock()
        mock_device = mocker.MagicMock()
        command = Command.from_data(
            mock_client,
            {
                'test-instance': {'value': 0, 'state': 'RCV'}
            },
            'test',
            mock_device
        )

        assert command.identifier == 'test'
        assert command.device == mock_device
        assert command.instances.get('test-instance').state == 'RCV'

    def test_command_execute(self, mocker, SmarterClientMock):
        mock_client = SmarterClientMock()
        mock_device = mocker.MagicMock(identifier='device-1')
        command = Command.from_data(
            mock_client,
            {
                'test-instance': {'value': 0, 'state': 'RCV'}
            },
            'test',
            mock_device
        )

        command.execute('user-1', 5)

        mock_client.send_command.assert_called_with(
            'device-1',
            'test',
            {'value': 5, 'user_id': 'user-1'})


class TestDevice:
    @pytest.fixture
    def device(self, SmarterClientMock):
        mock_client = SmarterClientMock()
        return Device.from_data(
            mock_client,
            {
                'commands': {
                    'test': {
                        'test-instance': {'value': 0, 'state': 'RCV'}
                    }
                },
                'settings': {
                    'network': 'network-1'
                },
                'status': {
                    'default': True
                }
            },
            'device-1'
        )

    def test_device_from_data_should_create_instance(self, device):

        assert device.identifier == 'device-1'
        assert device.commands.get('test').identifier == 'test'

    def test_watch_calls_client(self, mocker, device: Device, SmarterClientMock: Type[SmarterClient]):
        mock_client = SmarterClientMock()
        callback = mocker.Mock()
        device.watch(callback)

        mock_client.watch_device_attribute.assert_called_with(
            'device-1', mocker.ANY)

    def test_watch_calls_callback_on_event(self, mocker, device: Device, SmarterClientMock: Type[SmarterClient]):
        mock_client = SmarterClientMock()

        def watch_device_attribute_mock(id, callback):
            callback({'test': 'value'})
            return mocker.Mock()

        mock_client.watch_device_attribute.side_effect = watch_device_attribute_mock
        callback = mocker.Mock()
        device.watch(callback)

        callback.assert_called_with({'test': 'value'})

    def test_watch_twice_raises_error(self, mocker, device: Device, SmarterClientMock: Type[SmarterClient]):
        callback = mocker.Mock()
        device.watch(callback)

        with pytest.raises(RuntimeError):
            device.watch(callback)

    def test_unwatch_does_not_raise_error(self, mocker, device: Device, SmarterClientMock: Type[SmarterClient]):
        device.unwatch()

    def test_unwatch_closes_stream(self, mocker, device: Device, SmarterClientMock: Type[SmarterClient]):
        mock_client = SmarterClientMock()
        callback = mocker.Mock()
        mock_stream = mocker.MagicMock()
        mock_client.watch_device_attribute.return_value = mock_stream
        device.watch(callback)

        device.unwatch()

        mock_stream.close.assert_called()

    def test_fetch_calls_client(self, device: Device, SmarterClientMock: Type[SmarterClient]):
        mock_client = SmarterClientMock()
        device.fetch()

        mock_client.get_device.assert_called_with('device-1')

    def test_device_update_put(self, device: Device, SmarterClientMock: Type[SmarterClient], mocker):
        device_callback = {}
        watch_callback = mocker.Mock()
        stream_mock = mocker.MagicMock()
        mock_client = SmarterClientMock()

        def device_watch_mock(self, cb):
            device_callback['value'] = cb
        mock_client.watch_device_attribute.side_effect = device_watch_mock
        mock_client.watch_device_attribute.return_value = stream_mock

        device.watch(watch_callback)

        assert device_callback is not None
        device_callback['value']({
            'event': 'put',
            'path': 'status',
            'data': {'test': True}
        })

        assert device.status == {'test': True}

    def test_device_update_patch(self, device: Device, SmarterClientMock: Type[SmarterClient], mocker):
        device_callback = {}
        watch_callback = mocker.Mock()
        stream_mock = mocker.MagicMock()
        mock_client = SmarterClientMock()

        def device_watch_mock(self, cb):
            device_callback['value'] = cb
        mock_client.watch_device_attribute.side_effect = device_watch_mock
        mock_client.watch_device_attribute.return_value = stream_mock

        device.watch(watch_callback)

        assert device_callback is not None
        device_callback['value']({
            'event': 'patch',
            'path': 'status',
            'data': {'test': True}
        })

        assert device.status == {'default': True, 'test': True}

    def test_device_update_delete(self, device: Device, SmarterClientMock: Type[SmarterClient], mocker):
        device_callback = {}
        watch_callback = mocker.Mock()
        stream_mock = mocker.MagicMock()
        mock_client = SmarterClientMock()

        def device_watch_mock(self, cb):
            device_callback['value'] = cb
        mock_client.watch_device_attribute.side_effect = device_watch_mock
        mock_client.watch_device_attribute.return_value = stream_mock

        device.watch(watch_callback)

        assert device_callback is not None
        device_callback['value']({
            'event': 'put',
            'path': 'status',
            'data': None
        })

        assert device.status == {}


class TestLoginSession:
    def test_login_session_from_data_should_create_instance(self):
        with time_machine.travel(datetime.datetime.fromtimestamp(0, tz=ZoneInfo('UTC')), tick=False):
            session = LoginSession(
                {
                    'kind': 'test-kind',
                    'localId': 'test-id',
                    'email': 'test-email',
                    'displayName': 'test-display-name',
                    'idToken': 'test-token',
                    'registered': True,
                    'refreshToken': 'test-refresh',
                    'expiresIn': 100
                }
            )

            assert session.kind == 'test-kind'
            assert session.local_id == 'test-id'
            assert session.email == 'test-email'
            assert session.display_name == 'test-display-name'
            assert session.id_token == 'test-token'
            assert session.registered == True
            assert session.refresh_token == 'test-refresh'
            assert session.expires_at == datetime.datetime.fromtimestamp(100)

    def test_login_session_is_not_expired(self):
        with time_machine.travel(datetime.datetime.fromtimestamp(0, tz=ZoneInfo('UTC')), tick=False):
            session = LoginSession(
                {
                    'kind': 'test-kind',
                    'localId': 'test-id',
                    'email': 'test-email',
                    'displayName': 'test-display-name',
                    'idToken': 'test-token',
                    'registered': True,
                    'refreshToken': 'test-refresh',
                    'expiresIn': 100
                }
            )

            assert session.is_expired() == False

    def test_login_session_is_expired(self):
        with time_machine.travel(datetime.datetime.fromtimestamp(0, tz=ZoneInfo('UTC')), tick=False) as traveler:
            session = LoginSession(
                {
                    'kind': 'test-kind',
                    'localId': 'test-id',
                    'email': 'test-email',
                    'displayName': 'test-display-name',
                    'idToken': 'test-token',
                    'registered': True,
                    'refreshToken': 'test-refresh',
                    'expiresIn': 100
                }
            )

            traveler.shift(100)
            assert session.is_expired() == True

    def test_login_session_expires_in(self):
        with time_machine.travel(datetime.datetime.fromtimestamp(0, tz=ZoneInfo('UTC')), tick=False) as traveler:
            session = LoginSession(
                {
                    'kind': 'test-kind',
                    'localId': 'test-id',
                    'email': 'test-email',
                    'displayName': 'test-display-name',
                    'idToken': 'test-token',
                    'registered': True,
                    'refreshToken': 'test-refresh',
                    'expiresIn': 100
                }
            )

            assert session.expires_in == 100
            traveler.shift(90)
            assert session.expires_in == 10

    def test_login_session_update(self):
        with time_machine.travel(datetime.datetime.fromtimestamp(0, tz=ZoneInfo('UTC')), tick=False) as traveler:
            session = LoginSession(
                {
                    'kind': 'test-kind',
                    'localId': 'test-id',
                    'email': 'test-email',
                    'displayName': 'test-display-name',
                    'idToken': 'test-token',
                    'registered': True,
                    'refreshToken': 'test-refresh',
                    'expiresIn': 100
                }
            )

            traveler.shift(90)
            session.update({
                'idToken': 'new-token',
                'refreshToken': 'test-refresh'
            })

            assert session.id_token == 'new-token'
            assert session.expires_in == 100
            assert session.expires_at == datetime.datetime.fromtimestamp(190)

    def test_refresh_updates_time(self):
        with time_machine.travel(datetime.datetime.fromtimestamp(0, tz=ZoneInfo('UTC')), tick=False) as traveler:
            session = LoginSession(
                {
                    'kind': 'test-kind',
                    'localId': 'test-id',
                    'email': 'test-email',
                    'displayName': 'test-display-name',
                    'idToken': 'test-token',
                    'registered': True,
                    'refreshToken': 'test-refresh',
                    'expiresIn': 100
                }
            )

            traveler.shift(99)

            session.update({
                'idToken': 'new-token',
                'localId': 'test-id',
                'refreshToken': 'test-refresh',
            })

            assert session.expires_at == datetime.datetime.fromtimestamp(
                199)


class TestNetwork:
    pass


class TestSettings:
    pass


class TestStatus:
    pass


class TestUser:
    pass
