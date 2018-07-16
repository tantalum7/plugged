
from plugged.genericdevice import GenericDevice
from plugged.uri import Uri


class InternetGatewayDevice(GenericDevice):



    def __init__(self, location: Uri):
        super().__init__(location)



