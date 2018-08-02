
import xmltodict
from xml.etree import ElementTree
import requests
import zlib
from plugged.uri import Uri
from plugged.action import Action
from plugged.exceptions import *


class Device:

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
        self._actions = {}

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

    @property
    def actions(self):
        if not self._actions:
            self.get_actions()
        return self._actions

    def get_device_info(self):

        # Request device info
        infoXML, infoDict = self._soap_request(self.location)

        # Store device info
        self._name = infoDict["root"]["device"].get("friendlyName")
        self._manufacturer = infoDict["root"]["device"].get("manufacturer")
        self._model_description = infoDict["root"]["device"].get("modelDescription")
        self._model_number = infoDict["root"]["device"].get("modelNumber")
        self._serial_number = infoDict["root"]["device"].get("serialNumber")
        self._udn = infoDict["root"]["device"].get("UDN")

    def get_actions(self):

        # Init list
        action_list = set()

        # Request device info
        infoXML, infoDict = self._soap_request(self.location)

        # Find all the serviceLists throughout the xml doc (in different hierarchy levels)
        for service in infoXML.findall(".//*{urn:schemas-upnp-org:device-1-0}serviceList/"):


            service_resource = service.find('./{urn:schemas-upnp-org:device-1-0}SCPDURL').text

            serviceDict = self._soap_request_dict(self.location.copy(service_resource))

            service_resource = service.find('./{urn:schemas-upnp-org:device-1-0}controlURL').text
            service_type = service.find('./{urn:schemas-upnp-org:device-1-0}serviceType').text

            actions = serviceDict.get("scpd", {}).get("actionList", {}).get("action", [])
            actions = actions if isinstance(actions, list) else [actions]

            for action in actions:
                name = action.get("name", "")

                a = 0
                if "AddPortMapping" in name:
                    a = 10

                arguments = []
                return_values = []

                argument_list = action.get("argumentList", {}).get("argument", [])

                argument_list = argument_list if isinstance(argument_list, list) else [argument_list]

                for argument in argument_list:
                    if argument.get("direction") == "in":
                        arguments.append(argument.get("name", ""))
                    else:
                        return_values.append(argument.get("name", ""))

                action_list.add(Action(name=name, control_uri=self.location.copy(service_resource), arguments=arguments,
                                       return_values=return_values, service_type=service_type))

        self._actions = {action.name: action for action in action_list}


    def _soap_request(self, request_location: Uri):
        try:
            response_text = requests.get(request_location.get_url()).text
            return ElementTree.fromstring(response_text), xmltodict.parse(response_text)
        except ElementTree.ParseError as e:
            raise BadSoapResponse(e.msg)

    def _soap_request_dict(self, request_location):
        return xmltodict.parse(requests.get(request_location.get_url()).text)

    def __eq__(self, other):
        if isinstance(other, Device):
            return other.location == self.location

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._location.__hash__()