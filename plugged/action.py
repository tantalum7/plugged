
from plugged.uri import Uri


class Action:

    def __init__(self, name: str, control_uri: Uri, arguments: list):

        self.name = name
        self.control_uri = control_uri
        self.arguments = arguments

    def __eq__(self, other):
        if isinstance(other, Action):
            return hash(other) == hash(self)

    def __hash__(self):
        return hash(self.control_uri) + hash(self.name)

    def __repr__(self):
        return "Action({name}, {control_uri}, {arguments})".format(**self.__dict__)

    def __str__(self):
        return self.__repr__()