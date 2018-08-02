
import urllib
import urllib.parse
import zlib


class Uri:

    def __init__(self, scheme: str, hostname: str, port: int, resource: str):
        """ Simple Uri (Universal Resource Identifier) class to split/join uri components
            format: scheme://hostname:port/resource (e.g. http://stuff.com:1234/personal/addressbook.xml)"""
        self.scheme = scheme
        self.hostname = hostname
        self.port = port
        self.resource = resource

    @classmethod
    def parse(cls, url_string):
        """ Create a Uri instance by parsing a url string"""
        url = urllib.parse.urlsplit(url_string)
        return cls(scheme=url.scheme, hostname=url.hostname, port=url.port, resource=url.path)

    def get_url(self, resource=None):
        resource = resource if resource else self.resource
        fmt = "{scheme}://{hostname}:{port}{resource}" if self.port is not None else "{scheme}://{hostname}{resource}"
        return fmt.format(scheme=self.scheme, hostname=self.hostname, port=self.port, resource=resource)

    def get_root_url(self):
        fmt = "{scheme}://{hostname}:{port}" if self.port is not None else "{scheme}://{hostname}"
        return fmt.format(scheme=self.scheme, hostname=self.hostname, port=self.port)

    def copy(self, resource=None):
        resource = resource if resource else self.resource
        return Uri(scheme=self.scheme, hostname=self.hostname, port=self.port, resource=resource)

    def repr(self):
        return "Uri({scheme}, {hostname}, {port}, {resource}".format(**self.__dict__)

    def __str__(self):
        return self.get_url()

    def __hash__(self):
        return zlib.adler32(self.repr().encode())

    def __eq__(self, other):
        if isinstance(other, Uri):
            return other.__hash__() == self.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)