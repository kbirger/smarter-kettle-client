# from __future__ import annotations

# from unittest.mock import MagicMock
from typing import Type
from unittest.mock import MagicMock, Mock
import pytest
import pytest_mock


import sys
import types

from smarter_client.domain.models import Command, CommandInstance, Commands, Device, LoginSession
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
        callback = mocker.Mock()
        # device.watch(callback)
        device.unwatch()

    def test_unwatch_closes_stream(self, mocker, device: Device, SmarterClientMock: Type[SmarterClient]):
        mock_client = SmarterClientMock()
        callback = mocker.Mock()
        stream_close_mock = mocker.Mock()
        mock_client.watch_device_attribute.return_value = stream_close_mock
        device.watch(callback)

        device.unwatch()

        stream_close_mock.assert_called()

    def test_fetch_calls_client(self, device: Device, SmarterClientMock: Type[SmarterClient]):
        mock_client = SmarterClientMock()
        device.fetch()

        mock_client.get_device.assert_called_with('device-1')


class TestLoginSession:
    pass


class TestNetwork:
    pass


class TestSettings:
    pass


class TestStatus:
    pass


class TestUser:
    pass
