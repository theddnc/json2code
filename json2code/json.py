__author__ = 'jzaczek'

from enum import Enum
import re
from dateutil import parser as date_parser


class JSONValueType(Enum):
    integer = 1
    id = 2
    float = 3
    string = 4
    resource_uri = 5
    array = 6
    object = 7
    null = 8
    bool = 9
    date = 10
    invalid = -1


class JSONValueModel:
    def __init__(self, name, value):
        self.name = name
        self.v = value
        self.predicted_type = self.__predict_type()
        self.predicted_reference = self.__predict_reference()

    def __predict_type(self):
        if type(self.v) is int:
            if u"id" in self.name.lower():
                return JSONValueType.id
            return JSONValueType.integer
        if type(self.v) is unicode:
            if u"uri" in self.name.lower() or u"url" in self.name.lower():
                return JSONValueType.resource_uri   #todo actually try to parse the uri
            try:
                date = date_parser.parse(self.v)
                self.v = date
                return JSONValueType.date
            except ValueError:
                pass
            return JSONValueType.string
        if type(self.v) is float:
            return JSONValueType.float
        if type(self.v) is bool:
            return JSONValueType.bool
        if type(self.v) is None:
            return JSONValueType.null
        if type(self.v) is dict:
            return JSONValueType.object
        if type(self.v) is list:
            return JSONValueType.array

    def __predict_reference(self):
        if self.predicted_type == JSONValueType.resource_uri or self.predicted_type == JSONValueType.id:
            reference = self.name.lower()
            reference = re.sub("[_.]+(uris|uri)[_.]?", "", reference)
            reference = re.sub("[_.]+(ids|id)[_.]?", "", reference)

            return reference
        else:
            return None