
import requests
import xmltodict
from xml.etree import ElementTree
from plugged.uri import Uri
from plugged.exceptions import *

class Action:

    def __init__(self, name: str, control_uri: Uri, service_type: str, arguments: list, return_values: list):

        self.name = name
        self.control_uri = control_uri
        self.arguments = arguments
        self.return_values = return_values
        self.service_type = service_type

    def __eq__(self, other):
        if isinstance(other, Action):
            return hash(other) == hash(self)

    def __hash__(self):
        return hash(self.control_uri) + hash(self.name)

    def __repr__(self):
        return "Action({name}, {control_uri}, {arguments})".format(**self.__dict__)

    def __str__(self):
        return self.__repr__()

    def invoke(self, **kwargs):

        # Prepare soap action string
        soap_action = '"{service_type}#{name}"'.format(service_type=self.service_type, name=self.name)

        # Prepare arguments xml
        argument_xml = ""
        for argument in self.arguments:
            arg = kwargs[argument] if argument in kwargs else ""
            argument_xml += "<{name}>{value}</{name}>".format(name=argument, value=arg)

        # Prepare soap xml body
        body = ('<?xml version="1.0"?>'
                '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
                  '<s:Body>'
                    '<u:{name} xmlns:u="{service_type}">{argument_xml}</u:{name}>'
                  '</s:Body>'
                '</s:Envelope>\r\n').format(name=self.name, service_type=self.service_type, argument_xml=argument_xml)

        # Prepare headers
        headers = {"Content-Type": 'text/xml',
                   "SOAPAction": soap_action,
                   "Host": "{}:{}".format(self.control_uri.hostname, self.control_uri.port),
                   #"Content-Length": str(len(body)),
                   "Connection": "Close",
                   "Cache-Control": "no-cache",
                   "Pragma": "no-cache",
                   "Accept": None,
                   "Accept-Encoding": None,
                   }

        resp = requests.post(url=self.control_uri.get_url(), data=body.encode(), headers=headers)




        # If request fails (doesn't return status code 200), raise an exception
        if not resp:

            if "xml" in resp.headers["Content-Type"]:
                error_xml = ElementTree.fromstring(resp.text)
                code_xml = error_xml.find(".//{urn:schemas-upnp-org:control-1-0}errorCode")
                code = code_xml.text if code_xml is not None else ""
                description_xml = error_xml.find(".//{urn:schemas-upnp-org:control-1-0}errorDescription")
                description = description_xml.text if description_xml is not None else ""

            else:
                code = resp.status_code
                description = resp.text

            raise ActionRequestFailed("{}: {}".format(code, description))

        # Parse the response soap xml
        resp_xml = ElementTree.fromstring(resp.text)

        # Find the ActionResponse item in the xml response
        resp_values = resp_xml.find(('.//{{{service}}}{name}Response').format(service=self.service_type, name=self.name))

        # Grab return values, store in dict and return
        return {x.tag: x.text for x in resp_values}



