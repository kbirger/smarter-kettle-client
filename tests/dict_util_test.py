from copy import deepcopy
from typing import Generator
import pytest
from smarter_client.dict_util import delete_dict, patch_dict, put_dict


@pytest.fixture()
def original_state() -> Generator[dict, None, None]:
    yield {
        'commands': {
            'test_command': {
                'example': {
                    'state': 'NACK',
                    'value': 0
                }
            }
        },
        'notifications': {
            'user1': {
                'test': False
            }
        },
        'settings': {
            'network': 'test-id',
            'network_ssid': 'test'
        },
        'status': {
            'alarm_failed': 0,
            'alarms': {
                'alarm-id1': {
                    "active": False,
                    "auto_trigger": True,
                    "boil_temperature": 100,
                    "device": "000000000000",
                    "formula_mode_enable": True,
                    "formula_mode_temperature": 70,
                    "formula_mode_temps_locked": True,
                    "hour": 17,
                    "keep_warm_time": 5,
                    "minute": 0,
                    "notify": "Cycle starts",
                    "repeat": "S0M1T0W0T0F0S0",
                    "tone": "SMARTER",
                    "user": "user1",
                    "vendorId": "11111111111"
                }
            },
            "boil_temperature": 81,
            "boiled_keeping_warm": {
                "heating": True,
                "temperature": 100,
                "ts": 1711461225
            },
        }
    }


class TestPatchDict:
    def test_patch_to_empty_dict(self):
        assert patch_dict({}, 'a', {'a1': 1}) == {'a': {'a1': 1}}

    def test_patch_empty_dict_to_dict(self):
        assert patch_dict({'a': {'a1': 0}}, 'a', {}) == {'a': {'a1': 0}}

    def test_patch_empty_dict_to_dict_new_value(self):
        assert patch_dict({'a': {'a1': 0}}, 'b', {}) == {
            'a': {'a1': 0}, 'b': {}}

    def test_patch_dict_to_dict(self, original_state: dict):
        expected = deepcopy(original_state)
        expected['new'] = 1
        assert patch_dict(original_state, '/', {'new': 1}) == expected

    def test_creates_nested(self, original_state: dict):
        expected = deepcopy(original_state)
        expected['commands']['test_command']['test-instance'] = {
            'value': {'state': 'RCV'}
        }

        assert put_dict(
            original_state, 'commands/test_command/test-instance/value', {'state': 'RCV'}) == expected

    def test_deletes_nested(self, original_state: dict):
        expected = deepcopy(original_state)
        original_state['commands']['test_command']['test-instance'] = {
            'value': {'state': 'RCV'}
        }

        assert delete_dict(
            original_state, 'commands/test_command/test-instance', None) == expected

    def test_delete_root_error(self, original_state: dict):
        with pytest.raises(ValueError):
            delete_dict(original_state, '/')

    def test_put_root(self, original_state: dict):
        assert put_dict(original_state, '/', {'new': 1}) == {'new': 1}

    def test_nested_patch(self):
        assert patch_dict(
            {
                'a1': {
                    'a1b1': 0,
                    'a1b3': 0
                },
                'a2': {
                    'a2b1': 0
                }
            },
            'a1/a1b2',

            {'x1': 1}
        ) == {
            'a1': {
                'a1b1': 0,
                'a1b2': {'x1': 1},
                'a1b3': 0,
            },
            'a2': {
                'a2b1': 0,
            }
        }
