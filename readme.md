# Plugged

A lightweight Pythonic uPnP library, written entirely in python (py3.x)

Discover uPnP devices on the network:
```pythonstub
from plugged import Plugged
 
devices = Plugged.discover()
```

Grab the first router found (IGD device)
```pythonstub
router = Plugged.get_router()
```

View all uPnP actions available, and an action's arguments
```pythonstub
actions = device.actions
arg_list = actions["AddPortMapping"].arguments
```

Full example - add port mapping to router
```python
from plugged import Plugged
 
router = Plugged.get_router()
router.actions["AddPortMapping"].invoke(NewExternalPort="9000",
                                        NewProtocol="UDP",
                                        NewInternalPort="9000",
                                        NewInternalClient="192.168.1.6",
                                        NewEnabled="1",
                                        NewPortMappingDescription="plugged_port_add",
                                        NewLeaseDuration="0")
```

### Plugged Class (static)

```Plugged.FILTER_IGD``` : Filter string for searching for IGD (Internet Gateway Devices) only

```Plugged.FILTER_ALL``` : Standard accept all filter

```Plugged.discover(filter="ssdp:all", wait=3, repeat_count=3, ignore_dslforum_devices=True) -> [Device]```

Sends an SSDP broadcast (*repeat* times) across local network, and compiles response into a list of Devices after waiting for *wait* seconds for valid replies. Devices are filtered by *filter* string, which should be a valid uPnP M-SEARCH ST value. The default filter is all devices. Also uPnP devices can sometimes list duplicate devices, with dslforum protocols instead of uPnP, which can be ignored by setting *ignore_dslforum_devices* true.

```Plugged.get_router() -> Device```

Essentially a convenience function for ```Plugged.Discover(Plugged.FILTER_IGD)[0]``` it returns first device matching the IGD filter.

### Device Class

```
Device.location -> Uri
Device.name - > str
Device.manufacturer - > str
Device.model_description - > str
Device.model_name - > str
Device.serial_number - > str
Device.udn - > str
```
Read only descriptive device properties

```Device.actions -> {Action.name: Action}``` : Returns a dict of actions, indexed by action name

### Action Class

```
Action.name -> str
Action.control_uri -> Uri
Action.arguments -> [str]
Action.return_values -> [str]
```
Read only action properties

```Action.invoke(**kwargs) -> {str: str}```
Invokes the action, with the keyword arguments specified and returns a dict of return values. Raises ```ActionRequestFailed``` if device doesn't return a 200 OK response. The expected keyword arguments are in the ```Device.arguments``` list, and the return values in the ```Action.return_values``` list.

### Uri Class 

Simple class to store uri scheme, hostname, port and resource as separate items.

```
Uri.scheme -> str
Uri.hostname -> str
Uri.port -> int
Uri.resource -> str
```

Read/Write Uri properties

```Uri.parse(url_string:str) -> Uri``` Static method, parses a full url string (http://192.168.1.90:8080/pineapples.html) into a Uri object 

```Uri.get_url(resource: str=None) -> str``` Returns a url string (reverse of parse) for the uri object. Optional resource parameter to temporarily change the resource, but keep the rest the same.

```Uri.get_rool_url() -> str``` Returns the scheme, hostname and port only (http:192.168.1.90:8080)

```Uri.copy(resource: str=None) -> Uri``` Creates a duplicate Uri instance, optionally with a different resource


### Exceptions

```
ActionRequestFailed
ActionMissingParameters
BadSoapResponse
CannotFindDevice
```