from ncclient import manager
from dataclasses import dataclass
import argparse

@dataclass(frozen=True)
class IntBriefRow:
    name: str
    ip: str
    status: str
    protocol: str





def connect_to_device(host, port, username, password):
    m = manager.connect(
        host = host,
        port = port,
        username = username,
        password = password,
        hostkey_verify = False,
        device_params = {"name": "csr"},
    )
    print(f"Connected to {host}")
    return m

def terminate_connection(m):
    m.close_session()
    print("Connection terminated")
def grabbing_preset_data(m):
    my_filter = """
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface/>
      </interfaces-state>
    """
    response = m.get(filter=("subtree",my_filter))
    return response.xml




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Connecting to a device via NETCONF and executing RPC")
    parser.add_argument("--host", type = str, required = True, help = "Device IP address")
    parser.add_argument("--port", type = int, required = True, help = "Desired port connection")
    parser.add_argument("--user", type = str, required= True , help = "Define a server username used in connection")
    parser.add_argument("--password", type = str, required = True , help = "Define a password used in connection")

    args = parser.parse_args()

    my_session = connect_to_device(args.host,args.port,args.user,args.password)

    rows = grabbing_preset_data(my_session)
    print(rows)

    terminate_connection(my_session)




