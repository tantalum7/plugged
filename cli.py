
import argparse
import sys
import plugged


def add_port_mapping():
    # internalIP internalPort externalPort Protocol Description LeaseDuration
    parser = argparse.ArgumentParser()

    parser.add_argument("--internal_ip", "-i", help="Internal (local) IP for mapping")
    parser.add_argument("--internal_port", "-p", help="Internal (local) port for mapping (0 for random)", type=int)
    parser.add_argument("--external_port", "-e", help="External port for mapping (0 for random)", type=int)
    parser.add_argument("--protocol", "-u", help="UDP or TCP protocol for mapping rule", choices=["TCP", "UDP"])
    parser.add_argument("--description", "-d", help="Optional description for mapping rule")
    parser.add_argument("--duration", "-t", help="Rule duration in seconds (0 for unlimited)", type=int)

    args = parser.parse_args(sys.argv[2:])

    try:
        router = plugged.Plugged.get_router()
        router.actions["AddPortMapping"].invoke(NewExternalPort=args.external_port,
                                                NewProtocol=args.protocol,
                                                NewInternalPort=args.internal_port,
                                                NewInternalClient=args.internal_ip,
                                                NewEnabled="1",
                                                NewPortMappingDescription=args.description,
                                                NewLeaseDuration=args.duration)

    except Exception as e:
        print("ERROR")
        print(e)

    else:
        print("DONE")


if __name__ == "__main__":

    # AddPortMapping

    if "add_port_mapping" in sys.argv[1]:
        add_port_mapping()
    else:
        print("ERROR")
        print("Command not recognised")

    print("END")