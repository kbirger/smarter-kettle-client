from __future__ import annotations
from typing import Any, Dict

from smarter_kettle_client.domain import Device, SmarterClient
from smarter_kettle_client.managed_devices.base import BaseDevice


class SmarterKettleV3(BaseDevice):
    device: Device = None
    user_id: str = None
    _status_handler: Any = None

    @classmethod
    def from_id(cls, client: SmarterClient, device_id: str, user_id: str) -> SmarterKettleV3:
        device = Device.from_id(client, device_id)
        device.fetch()
        return cls(device, user_id)

    @classmethod
    def from_device(cls, device: Device, user_id: str) -> SmarterKettleV3:
        device.fetch()
        return cls(device, user_id)

    def __init__(self, device: Device, user_id: str):
        super().__init__(device, 'Smarter Kettle V3', 'kettle', user_id)

    def _on_event(self, event):
        if 'status' not in event.get('path', []):
            return

        if self._status_handler:
            self._status_handler(self.device.status)

    def _send_command(self, command: str, value: Any):
        self.device.commands.get(command).execute(self.user_id, value)

    @property
    def status(self):
        return self.device.status

    @property
    def settings(self):
        return self.device.settings

    def watch_status(self, handler: Any):
        self._status_handler = handler
        self.device.watch(self._on_event)

    def add_alarm(self, value: int):
        self._send_command('add_alarm', value)

    def calibrate_weight_sensor(self, value: int):
        self._send_command('calibrate_weight_sensor', value)

    def change_alarm(self, value: int):
        self._send_command('change_alarm', value)

    def remove_alarm(self, value: int):
        self._send_command('remove_alarm', value)

    def reset_settings(self, value: int):
        self._send_command('reset_settings', value)

    def resync_database(self, value: int):
        self._send_command('resync_database', value)

    def send_notification(self, value: int):
        self._send_command('send_notification', value)

    def send_ping(self, value: int):
        self._send_command('send_ping', value)

    def server_restart(self, value: int):
        self._send_command('server_restart', value)

    def set_boil_temperature(self, value: int):
        self._send_command('set_boil_temperature', value)

    def set_formula_mode_enable(self, value: bool):
        self._send_command('set_formula_mode_enable', value)

    def set_formula_mode_temperature(self, value: int):
        self._send_command('set_formula_mode_temperature', value)

    def set_handle_right_side(self, value: bool):
        self._send_command('set_handle_right_side', value)

    def set_keep_warm_time(self, value: int):
        self._send_command('set_keep_warm_time', value)

    def set_manual_boil_temperature(self, value: int):
        self._send_command('set_manual_boil_temperature', value)

    def set_manual_formula_mode_enable(self, value: bool):
        self._send_command('set_manual_formula_mode_enable', value)

    def set_manual_formula_mode_temperature(self, value: int):
        self._send_command('set_manual_formula_mode_temperature', value)

    def set_manual_keep_warm_time(self, value: int):
        self._send_command('set_manual_keep_warm_time', value)

    def set_options(self, value: int):
        self._send_command('set_options', value)

    def set_region(self, value: int):
        self._send_command('set_region', value)

    def set_user(self, value: Dict[str, Any]):
        self._send_command('set_user', value)

    def start_auto_boil(self):
        # Placeholder value, since no example provided
        self._send_command('start_auto_boil', 0)

    def start_boil(self, value: bool):
        self._send_command('start_boil', value)

    def stats_update(self, value: int):
        self._send_command('stats_update', value)

    def stop_boil(self, value: int):
        self._send_command('stop_boil', value)

    def turn_off_wifi(self, value: int):
        self._send_command('turn_off_wifi', value)
