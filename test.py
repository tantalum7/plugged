
from plugged import Plugged, Uri, InternetGatewayDevice


if __name__ == "__main__":

    igd = InternetGatewayDevice(Uri.parse("http://192.168.1.1:2555/upnp/InternetGatewayDevice:1/desc.xml"))
    igd.get_device_info()

    print("done")