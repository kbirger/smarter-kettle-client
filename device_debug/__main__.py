import asyncio
import sys
import time
from io import TextIOWrapper
from json import dumps
from pathlib import Path

import inquirer
from pynput.keyboard import Listener
from smarter_client.domain import SmarterClient
from smarter_client.domain.models import Device, User

username = None
password = None


def get_output_file():
    timestamp = int(time.time())
    report_path = Path(f"report-{timestamp}.json").resolve()

    return report_path


def get_credentials():
    credentialsPath = Path("credentials").resolve()
    if not credentialsPath.exists():
        print(f"Credentials file not found at {credentialsPath}")
        exit(1)

    print(f"Reading credentials file: {credentialsPath}")
    with open("credentials") as cred:
        try:
            (username, password) = cred.read().splitlines()
        except ValueError:
            print("Credentials file is not in correct format. One line with email, followed by one line with password.")

    return username, password


def sign_in(username, password):
    client = SmarterClient()
    session = client.sign_in(username, password)
    user = User.from_id(client, session.local_id)
    user.fetch()

    return user


def prompt_for_device(user):
    network_name = inquirer.prompt([inquirer.List("network", message="Select network", choices=user.networks)])[
        "network"
    ]
    network = user.networks[network_name]
    network.fetch()
    device_id = inquirer.prompt(
        [
            inquirer.List(
                "device", message="Select device", choices=[device.identifier for device in network.associated_devices]
            )
        ]
    )["device"]

    device = next(device for device in network.associated_devices if device.identifier == device_id)
    device.fetch()

    return device


class DeviceListener:
    device: Device
    log_file: TextIOWrapper | None = None
    is_listening: bool = False

    def __init__(self, device: Device):
        self.device = device

    def start(self):
        self.is_listening = True
        self.log_file = open(get_output_file(), "w")

        def on_status_change(event):
            if state := event["data"].get("state"):
                # state = event["data"]["state"]
                if state in ("RCV", "ACK", "FIN"):
                    return
            self.log_file.writelines([dumps(event)])
            print(event)

        self.device.watch(on_status_change)

    def stop(self):
        print("Stopping device listener")
        self.is_listening = False
        if self.log_file:
            self.log_file.close()

        self.device.unwatch()
        sys.exit(0)


def listen_for_key(device_listener: DeviceListener):
    def on_key_press(key):
        device_listener.stop()
        return True

    # Collect all event until released
    with Listener(on_press=on_key_press) as listener:
        listener.join()


async def main():
    username, password = get_credentials()
    user = sign_in(username, password)
    device = prompt_for_device(user)
    listener = DeviceListener(device)
    key_task = None

    print("Listening for events. Press any key to terminate")

    key_task = asyncio.to_thread(lambda: listen_for_key(listener))

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, listener.start)
    await key_task
    print("Finished.")


asyncio.run(main())
