# from __future__ import annotations

# from unittest.mock import MagicMock
from unittest.mock import MagicMock, Mock
import pytest
import pytest_mock


import sys
import types

from smarter_client.domain.models import Command, CommandInstance, Commands, LoginSession


# module_name = 'smarter_client'
# bogus_module = types.ModuleType(module_name)
# sys.modules[module_name] = bogus_module
# bogus_module.SmarterClient = MagicMock(name=module_name+'.SmarterClient')
# SmarterClient

@pytest.fixture
def SmarterClient(mocker):
    # return mocker.patch(
    #     'smarter_kettle_client.domain.smarter_client.SmarterClient',
    #     MagicMock(
    #         name='SmarterClient',

    #         wraps=False,
    #         new=False,
    #         spec={
    #             'sign_in': MagicMock()
    #         })
    # )
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
    pass
    # print(mocker)
    # print(pytest_mock.mocker)
    # return bogus_module.SmarterClient()

# from smarter_kettle_client.domain.models import Command, Commands  # nopep8


# @pytest.fixture
# def mock_client(mocker):
#     print(mocker)
#     print(pytest_mock.mocker)
#     return bogus_module.SmarterClient()


class TestCommands:
    # def from_data_creates_instance(self):
    #     commands: Commands = Commands.from_data(
    #         {'test': {'test-instance': {'value': {'state': 'RCV'}}}})

    #     assert commands.get('test') == isinstance(Command)
    pass

    def test_from_data(self, mocker, SmarterClient):
        client = SmarterClient()

        assert isinstance(
            Commands.from_data(
                client,
                {'test': {'test-instance': {'value': {'state': 'RCV'}}}},
                mocker.MagicMock()
            ),
            Commands
        )

    def test_commands(self, mocker, SmarterClient):
        mock_client = SmarterClient()
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


class TestCommandInstance:
    def test_from_data(self, mocker, SmarterClient):
        mock_client = SmarterClient()
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
    pass


class TestDevice:
    pass


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
