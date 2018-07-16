
import requests
import socket
import time
import xmltodict
from plugged.uri import Uri
from plugged.genericdevice import GenericDevice
from plugged.igd import InternetGatewayDevice

class Plugged:

    SSDP_BCAST = ("239.255.255.250", 1900)

    DEVICE_TYPES = {"internetgatewaydevice": InternetGatewayDevice}

    def __init__(self):
        self.locations = set()
        self.router_location = None

    def discover_igd(self):
        self.discover(filter="urn:schemas-upnp-org:device:InternetGatewayDevice:1")

    def discover(self, filter="upnp:rootdevice", wait=10):

        # Prepare discover ssdp packet
        ssdp_discover = ('M-SEARCH * HTTP/1.1\r\n'
                         'HOST: 239.255.255.250:1900\r\n'
                         'MAN: "ssdp:discover"\r\n'
                         'MX: 1\r\n'
                         'ST: %s\r\n\r\n' % filter)

        # Send discover packet 3 times (its udp so stuff gets lost), and fetch replies
        reply_list = self._ssdp_request(ssdp_discover, self.SSDP_BCAST, wait=wait, repeat_count=3)

        # Prepare device list
        devices = set()

        # Iterate through all the packets in the reply list
        for ssdp_packet in reply_list:

            # If there is a location in the dict, create a device and add it to the list
            if "location" in ssdp_packet:
                location = Uri.parse(ssdp_packet['location'])

                for device_type in self.DEVICE_TYPES.keys():
                    if device_type in location.resource.lower():
                        devices.add(self.DEVICE_TYPES[device_type](location))
                devices.add(GenericDevice(location))

        # Convert set back to list, and return
        return list(devices)





    def _find_services(self, device_location: Uri):

        # Init list
        service_locations = []

        # Fire off soap request, and store the response
        device_soap = self._soap_request(device_location)

        # Grab virtual device list
        virtual_device_list = device_soap["root"]["device"]["deviceList"]["device"]

        # Iterate through virtual devices
        for device in virtual_device_list:

            # Pull server from device
            service = device.get("serviceList", {}).get("service", {})

            # If service resource url is present, copy device_location but with this resource
            if "SCPDURL" in service:
                service_locations.append(device_location.copy(resource=service["SCPDURL"]))

            if "deviceList" in device:
                pass

        # Iterate through service locations
        for location in service_locations:

            service_soap = self._soap_request(location)

            pass

    def _parse_ssdp_packet(self, packet):

        # Split into a list of lines
        lines = packet.splitlines()

        # Prepare empty dict
        data_dict = {}

        # Iterate through each line
        for line in lines:

            # If there isn't a colon in this line, skip it
            if b':' not in line:
                continue

            # Grab the key by splitting on the first colon found, and force lower case and strip out fore/aft spaces
            key = line[0:line.find(b':')].lower().strip().decode()

            # Set the value as everything after the colon, and strip out fore/aft spaces
            value = line[len(key) + 1:].strip().decode()

            # Insert key:value pair into dict
            data_dict[key] = value

        # Return the dict
        return data_dict

    def _ssdp_request(self, packet, ip_port_tuple, wait=10, repeat_count=1, max_replies=999):

        if isinstance(packet, str):
            packet = packet.encode()

        # Start a context with a new UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

            # Set the socket to non-blocking
            sock.setblocking(0)

            # Send packet as many times as repeat count
            for _ in range(repeat_count):
                sock.sendto(packet, ip_port_tuple)

            # Wait number seconds passed for replies to be received
            time.sleep(wait)

            # Create an empty reply list
            reply_list = set()

            # Iterate through the max number of replies we want to process
            for _ in range(max_replies):

                # Try and receive a reply packet, parse and store in reply_list
                try:
                    reply_list.add(sock.recv(1024))

                # If we get a socket error, stop processing replies (probably no more replies)
                except socket.error:
                    break

            #  Parse all the replies, and return as a new list
            return [self._parse_ssdp_packet(reply) for reply in reply_list]

    def _soap_request(self, request_location: Uri) -> dict:
        return xmltodict.parse(requests.get(request_location.get_url()).text)
