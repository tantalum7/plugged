
import xmltodict
from xml.etree import ElementTree
import requests
from plugged.uri import Uri
from plugged.action import Action


class GenericDevice:

    def __init__(self, location: Uri):

        # Init class vars
        self._location = location
        self._name = ""
        self._manufacturer = ""
        self._model_description = ""
        self._model_number = ""
        self._model_name = ""
        self._serial_number = ""
        self._udn = ""
        self._actions = []

        # Grab device info
        self.get_device_info()

    @property
    def location(self):
        return self._location

    @property
    def name(self):
        return self._name

    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def model_description(self):
        return self._model_description

    @property
    def model_number(self):
        return self._model_number

    @property
    def model_name(self):
        return self._model_name

    @property
    def serial_numer(self):
        return self._serial_number

    @property
    def udn(self):
        return self._udn

    def get_device_info(self):

        # Init list
        action_list = set()

        # Request device info
        infoXML, infoDict = self._soap_request(self.location)

        # Store device info
        self._name = infoDict["root"]["device"].get("friendlyName")
        self._manufacturer = infoDict["root"]["device"].get("manufacturer")
        self._model_description = infoDict["root"]["device"].get("modelDescription")
        self._model_number = infoDict["root"]["device"].get("modelNumber")
        self._serial_number = infoDict["root"]["device"].get("serialNumber")
        self._udn = infoDict["root"]["device"].get("UDN")

        # Find all the serviceLists throughout the xml doc (in different hierarchy levels)
        for service in infoXML.findall(".//*{urn:schemas-upnp-org:device-1-0}serviceList/"):


            service_resource = service.find('./{urn:schemas-upnp-org:device-1-0}SCPDURL').text

            serviceDict = self._soap_request_dict(self.location.copy(service_resource))

            service_resource = service.find('./{urn:schemas-upnp-org:device-1-0}controlURL').text

            actions = serviceDict.get("scpd", {}).get("actionList", {}).get("action", [])
            actions = actions if isinstance(actions, list) else [actions]

            for action in actions:
                name = action.get("name", "")

                arguments = []

                argument_list = action.get("argumentList", {}).get("argument", [])

                argument_list = argument_list if isinstance(argument_list, list) else [argument_list]

                for argument in argument_list:
                    arguments.append(argument.get("name", ""))

                action_list.add(Action(name=name, control_uri=self.location.copy(service_resource), arguments=arguments))

        self._actions = list(action_list)


    def get_actions(self):

        # Init list
        service_locations = []

        # Fire off soap request, and store the response
        device_soap = self._soap_request(self.location)

        # Grab virtual device list
        virtual_device_list = device_soap["root"]["device"]["deviceList"]["device"]

        # Iterate through virtual devices
        for device in virtual_device_list:

            # Pull server from device
            service = device.get("serviceList", {}).get("service", {})

            # If service resource url is present, copy device_location but with this resource
            if "SCPDURL" in service:
                service_locations.append(self.location.copy(resource=service["SCPDURL"]))

            if "deviceList" in device:
                pass

        # Iterate through service locations
        for location in service_locations:

            service_soap = self._soap_request(location)

            pass

    def _soap_request(self, request_location: Uri):
        response_text = requests.get(request_location.get_url()).text
        return ElementTree.fromstring(response_text), xmltodict.parse(response_text)

    def _soap_request_dict(self, request_location):
        return xmltodict.parse(requests.get(request_location.get_url()).text)

    def __eq__(self, other):
        if isinstance(other, GenericDevice):
            return other.location == self.location

    def __hash__(self):
        return self.location.__hash__()