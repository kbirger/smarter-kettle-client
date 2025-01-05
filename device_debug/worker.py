import asyncio
import multiprocessing
import multiprocessing.synchronize
import sys
import time
from collections.abc import Callable
from io import TextIOWrapper
from json import dumps
from pathlib import Path
from typing import Any

from smarter_client.domain import SmarterClient
from smarter_client.domain.models import Device

username = None
password = None


def get_output_file():
    timestamp = int(time.time())
    return Path(f"report-{timestamp}.json").resolve()


def sign_in(username, password):
    client = SmarterClient()
    client.sign_in(username, password)

    return client


def get_device(client: SmarterClient, device_id: str):
    device = Device.from_id(client, device_id)
    device.fetch()

    return device


class DeviceListener:
    device: Device
    log_file: TextIOWrapper | None = None
    is_listening: bool = False

    def __init__(self, device: Device, cb: Callable[[Any], None]):
        self.device = device
        self.cb = cb

    def start(self):
        self.is_listening = True
        self.log_file = open(get_output_file(), "w")

        def on_status_change(event):
            data = event["data"]

            if isinstance(data, dict):
                if data.get("state") in ("RCV", "ACK", "FIN"):
                    return
            self.cb(event)
            self.log_file.writelines([dumps(event)])
            self.log_file.flush()
            # print(event)

        self.device.watch(on_status_change)

    def stop(self):
        self.cb("[worker] Closing log file")
        self.is_listening = False
        if self.log_file:
            self.log_file.close()

        self.cb("[worker] Stopping device listener")
        self.device.unwatch()
        self.cb("[worker] Device listener stopped")
        self.cb(False)
        sys.exit(0)


def main(
    close_event: multiprocessing.synchronize.Event,
    output_pipe,
    username: str,
    password: str,
    device_id: str,
):
    # Run the work in an asyncio event loop
    # This is done so that we can start a thread to listen to the close_event
    try:
        asyncio.run(do_work(close_event, output_pipe, username, password, device_id))
    except KeyboardInterrupt:
        output_pipe.send("[worker] Keyboard interrupt")


async def do_work(
    close_event: multiprocessing.synchronize.Event,
    output_pipe,
    username: str,
    password: str,
    device_id: str,
):
    """
    Listen to the specified device and send events to the output pipe.

    :param close_event: Event to signal the worker to stop
    :param output_pipe: Pipe to send events to the main process
    :param username: Username to sign in with
    :param password: Password to sign in with
    :param device_id: Device ID to listen to
    """
    output_pipe.send("[worker] Starting")

    user = sign_in(username, password)
    device = get_device(user, device_id)
    listener = DeviceListener(device, lambda event: output_pipe.send(event))

    def waiter():
        # Block until close_event is set and then stop the listener
        output_pipe.send("[worker] Waiting for close event")
        close_event.wait()
        output_pipe.send("[worker] Shutting down")
        listener.stop()

    listener.start()

    # Wait for the close event to be set and perform graceful shutdown
    await asyncio.to_thread(waiter)
