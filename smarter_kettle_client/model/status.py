from typing import OrderedDict

from ..smarter_client import SmarterClient


class Status:
    def __init__(self, client: SmarterClient, data: OrderedDict):
        self.client = client
        self.alarm_failed = data.get('alarm_failed')
        # self.alarms = Alarms(client, data.get('alarms'))
        self.boil_temperature = data.get('boil_temperature')
