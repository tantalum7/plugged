
from plugged import Plugged, Uri


if __name__ == "__main__":


    router = Plugged.get_router()

    #r = router.actions["GetExternalIPAddress"].invoke()

    a = router.actions

    #r = router.actions["GetGenericPortMappingEntry"].invoke(NewPortMappingIndex="0")

    r = router.actions["AddPortMapping"].invoke(NewExternalPort="9000",
                                                NewProtocol="UDP",
                                                NewInternalPort="9000",
                                                NewInternalClient="192.168.1.6",
                                                NewEnabled="1",
                                                NewPortMappingDescription="python-stuff",
                                                NewLeaseDuration="0")
    """
    ('NewExternalPort', '35000'),  # specify port on router
    ('NewProtocol', 'TCP'),  # specify protocol
    ('NewInternalPort', '35000'),  # specify port on internal host
    ('NewInternalClient', '192.168.1.90'),  # specify IP of internal host
    ('NewEnabled', '1'),  # turn mapping ON
    ('NewPortMappingDescription', 'Test desc'),  # add a description
    ('NewLeaseDuration', '0')]  # how long should it be opened?
    """
    print("done")