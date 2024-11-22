import itertools
import json
from pathlib import Path

from smarter_client.domain.models import Commands, Network, User
from smarter_client.domain.smarter_client import SmarterClient

username = None
password = None

credentialsPath = Path("credentials").resolve()
report_path = Path("report").resolve()
if not credentialsPath.exists():
    print(f"Credentials file not found at {credentialsPath}")
    exit(1)

print(f"Reading credentials file: {credentialsPath}")
with open("credentials") as cred:
    try:
        (username, password) = cred.read().splitlines()
    except ValueError:
        print("Credentials file is not in correct format. One line with email, followed by one line with password.")


def load_from_network(client: SmarterClient, network: Network):
    """Load devices from a network."""
    network.fetch()
    for device in network.associated_devices:
        device.fetch()
        yield device


client = SmarterClient()

session = client.sign_in(username, password)

report = {}

user: User = User.from_id(client, session.local_id)
user.fetch()
devices = list(itertools.chain.from_iterable(load_from_network(client, network) for network in user.networks.values()))


def str_cmds(commands: Commands):
    """Serialize commands."""
    for command in commands.items():
        yield {"name": command[0], "data": command[1]._data}


report["devices"] = [
    {"id": device.identifier, "status": device.status, "commands": list(str_cmds(device.commands))}
    for device in devices
]

report_str = json.dumps(report, indent=2)
print(report_str)

print(f"Writing report to {report_path}")
with open(report_path, "w") as out_file:
    out_file.write(report_str)
