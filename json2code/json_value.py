__author__ = 'jzaczek'

from enum import Enum
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

    @classmethod
    def get_str_for_type(cls, type):
        if type is JSONValueType.integer:
            return "int"
        if type is JSONValueType.string:
            return "string"
        if type is JSONValueType.bool:
            return "bool"
        if type is JSONValueType.date:
            return "date"
        if type is JSONValueType.float:
            return "float"
        if type is JSONValueType.object:
            return "object"
        if type is JSONValueType.array:
            return "array"

        return None

    @classmethod
    def get_conf_str_for_ref_type(cls, type, str):
        if type is JSONValueType.object:
            return u"{0}:full".format(str)
        if type is JSONValueType.id:
            return u"{0}:id".format(str)
        if type is JSONValueType.resource_uri:
            return u"{0}:uri".format(str)

        return None

    @classmethod
    def get_conf_str_for_val_type(cls, value, str):
        if type(value) is dict:
            return u"{0}:full".format(str)
        if type(value) is int:
            return u"{0}:id".format(str)
        if type(value) is unicode:
            return u"{0}:uri".format(str)

        return None


referencing_types = [JSONValueType.id, JSONValueType.resource_uri, JSONValueType.array, JSONValueType.object]


class JSONValueModel:
    def __init__(self, name, value, **kwargs):
        self.predict_references = kwargs.get("predict_references", False)
        self.name = unicode(name)
        self.v = value
        self.predicted_type = self.__predict_type()
        self.predicted_references = None

    def __predict_type(self):
        if type(self.v) is int:
            if self.predict_references \
                    and u"id" != self.name.lower() \
                    and u"id" in self.name.lower():

                return JSONValueType.id
            return JSONValueType.integer
        if type(self.v) is unicode:
            if self.predict_references \
                    and u"resource_uri" != self.name.lower() \
                    and u"uri" in self.name.lower() or u"url" in self.name.lower():

                return JSONValueType.resource_uri   # todo actually try to parse the uri
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

    # def __predict_reference(self):
    #     if self.predicted_type == JSONValueType.resource_uri or self.predicted_type == JSONValueType.id \
    #             or self.predicted_type == JSONValueType.array:
    #         reference = self.name.lower()
    #         reference = re.sub("[_.]+(uri)[_.]?", "", reference)
    #         reference = re.sub("[_.]+(id)[_.]?", "", reference)
    #
    #         return reference
    #     else:
    #         return None