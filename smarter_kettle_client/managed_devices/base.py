from smarter_kettle_client.domain.models import Device
from abc import ABCMeta
from abc import abstractmethod


class BaseDevice(metaclass=ABCMeta):
    device: Device
    friendly_name: str
    type: str
    user_id: str

    def __init__(self, device: Device, friendly_name: str, type: str, user_id: str):
        device.fetch()
        self.device = device
        self.friendly_name = friendly_name
        self.user_id = user_id
        self.type = type

    @property
    def id(self):
        return self.device.identifier

    @property
    def model(self):
        return self.device.status.get('device_model')

    def firmware_version(self):
        return self.device.status.get('firmware_version')

    def __str__(self):
        return f"Device ID: {self.id}, Device Name: {self.friendly_name} ({self.model}), Device Type: {self.type}"
