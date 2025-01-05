"""
This script listens to events for a particular device and logs them to a file.

multiprocessing is used because the underlying library pyrebase uses SocketIO, which uses winsock on Windows,
which prevents normal graceful shutdown via the `signal` package.

Instead, this main script starts a separate process and communicates via pipes and an event to signal the worker to stop
when the main process receives a CTRL+C signal.


Usage:
    - Create a file named `credentials` in the root of the repository with the email and password on separate lines.
    - From the root of the repository:

      pip install -r device_debug/requirements.txt
      python -m device_debug
    - Follow the prompts to select a network and device to monitor.
    - Press CTRL+C to stop monitoring.
    - Inspect the generated report-*.log file

"""

import signal
from multiprocessing import Manager, Pipe, Process
from pathlib import Path

import device_debug.worker
import inquirer
from smarter_client.domain import SmarterClient
from smarter_client.domain.models import User

username = None
password = None


def get_credentials():
    credentialsPath = Path("credentials").resolve()
    if not credentialsPath.exists():
        print(f"[main] Credentials file not found at {credentialsPath}")
        exit(1)

    print(f"[main] Reading credentials file: {credentialsPath}")
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


if __name__ == "__main__":
    username, password = get_credentials()
    user = sign_in(username, password)
    device = prompt_for_device(user)

    with Manager() as manager:
        print("Press CTRL+C at any time to stop monitoring.")

        # Event to signal the worker to stop
        close_event = manager.Event()

        # Read and write pipes to communicate to other process
        r, w = Pipe()

        worker = Process(target=device_debug.worker.main, args=(close_event, w, username, password, device.identifier))

        # Callback to receive CTRL+C signal
        def stop(*args):
            print("[main] Stopping worker")
            close_event.set()
            try:
                worker.join()
            except AssertionError:
                pass
            return True

        signal.signal(signal.SIGINT, stop)

        # Start the worker and continue
        worker.start()

        # Print all messages received from the worker
        while True:
            msg = r.recv()
            if msg:
                print(msg)
            else:
                break
        print("[main] Gracefully shut down")
        exit(0)
