from smarter_kettle_client.domain import Network, Device, SmarterClient
from smarter_kettle_client.managed_devices.kettle_v3 import SmarterKettleV3


def load_from_network(network: Network, user_id: str) -> list[Device]:
    return (
        wrapper for wrapper in
        (
            get_device_wrapper(device, user_id)
            for device in network.associated_devices
        )
        if wrapper is not None
    )


def get_device_wrapper(device: Device, user_id: str):
    device.fetch()
    model = device.status.get('device_model')
    match model:
        case 'SMKET01':
            return SmarterKettleV3.from_device(device, user_id)
        case _:
            print(f'Unknown device model: {model}')
