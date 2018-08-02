
import requests
import socket
import time
import xmltodict
from plugged.uri import Uri
from plugged.device import Device
from plugged.exceptions import *


class Plugged:

    FILTER_IGD = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"
    FILTER_ALL = "ssdp:all"
    _SSDP_BCAST = ("239.255.255.250", 1900)

    @classmethod
    def discover(cls, filter="ssdp:all", wait=3, repeat_count=3, ignore_dslforum_devices=True) -> [Device]:
        """
        Discovers UPnP devices on the LAN, using the filer provided (defaults to all devices).
        Method sleeps for [wait] seconds to allow response to come in (blocking).
        M-SEARCH packet is send [repeat_count] times as its not reliable comms.
        Returns a list of plugged.Device
        :return:
        """
        # Prepare discover ssdp packet
        ssdp_discover = ('M-SEARCH * HTTP/1.1\r\n'
                         'HOST: 239.255.255.250:1900\r\n'
                         'MAN: "ssdp:discover"\r\n'
                         'MX: 1\r\n'
                         'ST: %s\r\n\r\n' % filter)

        # Send discover packet 3 times (its udp so stuff gets lost), and fetch replies
        reply_list = cls._ssdp_request(ssdp_discover, cls._SSDP_BCAST, wait=wait, repeat_count=repeat_count)

        # Prepare device list
        devices = set()

        # Iterate through all the packets in the reply list
        for ssdp_packet in reply_list:

            # If there is a location in the dict, create a device and add it to the list
            if "location" in ssdp_packet:

                # If ignore dslform devices is enabled, and dslforum is in the location string, skip it
                if ignore_dslforum_devices and "dslforum" in ssdp_packet['location']:
                    continue

                try:
                    devices.add(Device(Uri.parse(ssdp_packet['location'])))
                except BadSoapResponse:
                    continue

        # Convert set back to list, and return
        return list(devices)

    @classmethod
    def get_router(cls):

        # Discover all IGD devices
        devices = cls.discover(filter=cls.FILTER_IGD)

        # If we get nothing back, raise an exception
        if len(devices) == 0:
            raise CannotFindDevice()

        # Return the first result as the router
        return devices[0]

    @staticmethod
    def _parse_ssdp_packet(packet) -> dict:

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

    @classmethod
    def _ssdp_request(cls, packet, ip_port_tuple, wait=10, repeat_count=1, max_replies=999) -> list:

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
            return [cls._parse_ssdp_packet(reply) for reply in reply_list]

    @staticmethod
    def _soap_request(request_location: Uri) -> dict:
        return xmltodict.parse(requests.get(request_location.get_url()).text)
