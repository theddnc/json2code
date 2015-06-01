import copy
import re
from cdm_generator import ORIGIN_KEY
from parser import Parser
import utils
import os
from scanner import UnexpectedTokenException, TokenMismatchException

__author__ = 'jzaczek'

SWIFT_TYPES_MAP = {
    "int": "Int",
    "float": "Double",
    "string": "String",
    "date": "NSDate",
    "bool": "Bool",
    "object": "[String: JSON]",
    "array": "[JSON]"
}

SWIFTY_JSON_TYPES_MAP = {
    "int": "intValue",
    "float": "doubleValue",
    "string": "stringValue",
    "date": "stringValue",
    "bool": "boolValue",
    "object": "dictionaryValue",
    "array": "arrayValue"
}

DISCLAIMER = "// Please note that the code below is automatically generated and may be \n" \
             "// incomplete or redundant. Please make sure to verify these class \n" \
             "// specifications and apply proper changes to lines marked by comments. \n" \
             "//\n" \
             "// Thanks for using json2code!\n"


class CodeGenerator:
    def __init__(self, config_location, **kwargs):
        if not config_location.endswith("/"):
            config_location += "/"

        self.built_in_types_map = kwargs.get("types_map", SWIFT_TYPES_MAP)
        self.config_location = config_location
        self.file_names = []
        self.parsed_values = []
        self.file_name_key = utils.get_random_string(50)
        self.__load_files()

    def __load_files(self):
        try:
            for file_name in os.listdir(self.config_location):
                if file_name.endswith(".json"):
                    self.file_names.append(file_name)
        except OSError as e:
            print e
            return

        file_name = ""  # silences ide warning
        try:
            for file_name in self.file_names:
                parser = Parser(file_name=self.config_location+file_name, simple_value=True)
                parser.parse_json()
                result = parser.result
                result[self.file_name_key] = file_name
                self.parsed_values.append(result)
        except UnexpectedTokenException as e:
            print "Error in file {0}:\n".format(file_name)
            print e
            return
        except TokenMismatchException as e:
            print "Error in file {0}:\n".format(file_name)
            print e
            return

    def generate(self):
        output = DISCLAIMER + "\n\n"
        for parsed_value in self.parsed_values:
            class_name = utils.to_camel_case(parsed_value[self.file_name_key][0:-5], capital=True)
            origin = ""
            if ORIGIN_KEY in parsed_value:
                origin = "which was generated from json file: {0}".format(parsed_value[ORIGIN_KEY])
            parsed_value.pop(ORIGIN_KEY, None)
            output += "// generated from config file: {0} {1}\n".format(parsed_value[self.file_name_key], origin)
            output += "class {0}".format(class_name) + " {\n"
            parsed_value.pop(self.file_name_key, None)

            to_json_body = ""
            from_json_body = ""

            for key in parsed_value:
                value = parsed_value[key]

                #key = self.__remove_id_and_uri(key)
                member_declaration = self.__get_member_declaration(key, value)
                to_json = self.__get_to_json_conversion(key, value)
                from_json = self.__get_from_json_conversion(key, value)

                to_json_body += "\t\t{0}\n".format(to_json)
                from_json_body += "\t\t{0}\n".format(from_json)
                output += "\t{0}\n".format(member_declaration)

            output += "\n"

            to_json = self.__add_to_json_method(to_json_body)
            from_json = self.__add_from_json_method(from_json_body, class_name)
            output += "{0}\n\n{1}\n".format(from_json, to_json)

            output += "}\n\n"

        print output

    def __get_member_declaration(self, key, value):
        # exception for fields describing objects themselves, not other references to other objects
        member_name = utils.to_camel_case(key)

        if value.startswith(u"["):
            member_type = self.__get_member_type(value[1:-1], True)
        else:
            member_type = self.__get_member_type(value)

        member_declaration = "var {0}: {1}".format(member_name, member_type)

        return member_declaration

    def __get_member_type(self, value, array=False):
        if value.startswith(u":"):
            return self.__get_member_user_type(value[1:], array)
        else:
            return self.__get_member_built_in_type(value, array)

    def __get_member_built_in_type(self, value, array=False):
        built_in_type = self.built_in_types_map.get(value, None)
        if built_in_type is None:
            raise ConfigurationFileException("Error parsing value: {0}.\nAcceptable built-in types are:{1}".
                                             format(value, self.built_in_types_map.keys()))
        else:
            if array:
                built_in_type = "[{0}?]".format(built_in_type)
            else:
                built_in_type += "?"

        return built_in_type

    @classmethod
    def __add_from_json_method(cls, body, name):
        function = "\tclass func fromJson(json: JSON) -> {0} ".format(name) + "{\n"
        function += "\t\tvar newObject = {0}()\n".format(name)
        function += body
        function += "\t\treturn newObject\n"
        function += "\t}"

        return function

    @classmethod
    def __add_to_json_method(cls, body):
        function = "\tfunc toJson() -> JSON {\n"
        function += "\t\tvar json: JSON = JSON({})\n"
        function += body
        function += "\t\treturn json\n"
        function += "\t}"

        return function

    @classmethod
    def __get_member_user_type(cls, value, array=False):
        ref_type, possible_refs = cls.__get_possible_refs(value)

        if ref_type == u"full":
            output = utils.to_camel_case(possible_refs[0], capital=True) + "?"
            if array:
                output = "[{0}]".format(output)
            del possible_refs[0]

            if len(possible_refs) > 0:
                output += "\t//"
                for ref in possible_refs:
                    output += " or " + utils.to_camel_case(ref, capital=True) + "?"
                output += " - please choose appropriate type"
        elif ref_type == u"id":
            output = "Int?"
        elif ref_type == u"uri":
            output = "String?"
        else:
            output = ""

        return output

    @classmethod
    def __get_to_json_conversion(cls, key, value):
        if value.startswith(u":"):
            to_json = cls.__get_smart_to_json_conversion(key, value[1:])
        elif value.startswith(u"["):
            to_json = cls.__get_smart_to_json_conversion_for_array(key, value[2:-1])
        else:
            to_json = "json[\"{0}\"].{1} = self.{2}".format(key, SWIFTY_JSON_TYPES_MAP[value], utils.to_camel_case(key))
        if value == u"date":
            to_json = "//" + to_json + "\t// please add appropriate conversion!"

        return to_json

    @classmethod
    def __get_from_json_conversion(cls, key, value):
        if value.startswith(u":"):
            from_json = cls.__get_smart_from_json_conversion(key, value[1:])
        elif value.startswith(u"["):
            from_json = "newObject.{0} = []\n".format(utils.to_camel_case(key))
            from_json += "\t\tfor subJson in json[\"{0}\"] ".format(key) + "{\n"
            from_json += "\t\t\t" + cls.__get_smart_from_json_conversion(key, value[2:-1], "subJson", True)
            from_json += "\n\t\t}"
        else:
            from_json = "newObject.{0} = json[\"{1}\"].{2}".format(utils.to_camel_case(key), key, SWIFTY_JSON_TYPES_MAP[value])
        if value == u"date":
            from_json = "//" + from_json + "\t// please add appropriate conversion!"

        return from_json

    @classmethod
    def __get_smart_from_json_conversion(cls, key, value, json_name="json", array=False):
        ref_type, possible_refs = cls.__get_possible_refs(value)

        if array:
            from_json = "newObject.{0}.append(".format(utils.to_camel_case(key))
        else:
            from_json = "newObject.{0} = ".format(utils.to_camel_case(key))

        if ref_type == u"full":
            from_json += "{0}.fromJson({1}[\"{2}\"]!)".format(utils.to_camel_case(possible_refs[0], capital=True), json_name, key)
            if array:
                from_json += ") "
            from_json += cls.__get_other_possible_refs(possible_refs)
        elif ref_type == u"id":
            from_json += "{0}[\"{1}\"].intValue".format(json_name, key)
            if array:
                from_json += ")\n"
        elif ref_type == u"uri":
            from_json += "{0}[\"{1}\"].stringValue".format(json_name, key)
            if array:
                from_json += ")\n"
        else:
            raise ConfigurationFileException("Wrong reference type specified for key {0}: {1}. Use: [full, id, uri]"
                                             .format(key, ref_type))

        return from_json

    @classmethod
    def __get_smart_to_json_conversion(cls, key, value):
        ref_type, possible_refs = cls.__get_possible_refs(value)

        to_json = "json[\"{0}\"]".format(key)

        if ref_type == u"full":
            to_json += " = self.{0}.toJson() ".format(utils.to_camel_case(key, capital=False))
            del possible_refs[0]
            to_json += cls.__get_other_possible_refs(possible_refs)
        elif ref_type == u"id":
            to_json += ".intValue = self.{0}".format(utils.to_camel_case(key))
        elif ref_type == u"uri":
            to_json += ".stringValue = self.{0}".format(utils.to_camel_case(key))
        else:
            raise ConfigurationFileException("Wrong reference type specified for key {0}: {1}. Use: [full, id, uri]"
                                             .format(key, ref_type))
        return to_json

    @classmethod
    def __get_smart_to_json_conversion_for_array(cls, key, value):
        ref_type, possible_refs = cls.__get_possible_refs(value)
        if ref_type == u"full":
            to_json = "var {0}Array = [JSON]()\n".format(utils.to_camel_case(key))
            to_json += "\t\tfor obj in self.{0}".format(utils.to_camel_case(key)) + " {\n"
            to_json += "\t\t\t {0}Array.append(obj.toJson())\n".format(utils.to_camel_case(key))
            to_json += "\t\t}\n"
            to_json += "\t\tjson[\"{0}\"] = {1}Array".format(key, utils.to_camel_case(key))
            return to_json
        else:
            return "json[\"{0}\"].arrayValue = self.{1}".format(key, utils.to_camel_case(key))


    @classmethod
    def __get_possible_refs(cls, value):
        possible_refs = value.split(u":")
        ref_type = possible_refs[-1]
        del possible_refs[-1]
        return copy.copy(ref_type), copy.copy(possible_refs)

    @classmethod
    def __get_other_possible_refs(cls, refs):
        del refs[0]
        result = ""
        if len(refs) > 0:
            result = "\t// or "
            for ref in refs:
                result += "{0} ".format(utils.to_camel_case(ref, capital=True))
            result += "- please choose appropriate conversion"

        return result

    @classmethod
    def __remove_id_and_uri(cls, key):
        if key != u"id" and key != u"resource_uri":
            key = re.sub("[_.]+(uri)[_.]?", "", key)
            key = re.sub("[_.]+(id)[_.]?", "", key)

        return key


class ConfigurationFileException(Exception):
    pass

if __name__ == "__main__":
    generator = CodeGenerator("/Users/jzaczek/Documents/Projekty/WEiTI/TKOM/json_configs")
    generator.generate()