import copy
import os
from json_value import JSONValueType, JSONValueModel, referencing_types
from parser import Parser
from scanner import UnexpectedTokenException, TokenMismatchException

__author__ = 'jzaczek'

ORIGIN_KEY = u"!@#$ORIGIN$#@!"


class CDMGenerator:
    def __init__(self, json_examples_location, cdm_location, **kwargs):
        self.predict_references = kwargs.get("predict_references", False)
        self.file_location = json_examples_location
        if not self.file_location.endswith("/"):
            self.file_location += "/"
        self.output_location = cdm_location
        self.file_names = []
        self.cdm_entities = []

        self.__load_files()

    def generate(self):
        self.__flatten_queue()
        for i, entity in enumerate(self.cdm_entities):
            entity_v = entity.value.v
            for field_name in entity_v:
                if self.predict_references:
                    if entity_v[field_name].predicted_type in referencing_types:
                        entity_v[field_name].predicted_references = self.__find_matches(field_name)

            self.cdm_entities[i] = CDMEntity(JSONValueModel(entity.value.name, entity_v), entity.file_name)

        for cdm_entity in self.cdm_entities:
            cdm_entity.generate(self.output_location, predict_references=self.predict_references)

    def __find_matches(self, field_name):
        possible_matches = field_name.lower().split(u"_")
        possible_matches = [unicode(x) for x in possible_matches if x not in [u"uri", u"id", u"ids", u"uris"]]
        possible_matches.append(unicode(field_name.lower()))
        for match in possible_matches:
            if match.endswith(u"s"):
                possible_matches.append(match[:-1])

        matches = []
        for match in possible_matches:
            entity_names = [x.value.name.lower() for x in self.cdm_entities]
            if match in entity_names:
                matches.append(match)

        return matches

    def __load_files(self):
        try:
            for file_name in os.listdir(self.file_location):
                if file_name.endswith(".json"):
                    self.file_names.append(file_name)
        except OSError as e:
            print e
            return

        file_name = ""  # silences ide warning
        try:
            for file_name in self.file_names:
                parser = Parser(
                    file_name=self.file_location+file_name,
                    simple_value=False,
                    predict_references=self.predict_references)

                parser.parse_json()
                if len(self.cdm_entities) > 0:
                    for cdm_entity in self.cdm_entities:
                        if cdm_entity.value.name == file_name[0:-5]:
                            raise DataExampleException("Found same entity twice while loading! Entity: {0}".
                                                       format(file_name[0:-5]))

                cdm_entity = JSONValueModel(file_name[0:-5], parser.result)
                self.cdm_entities.append(CDMEntity(cdm_entity, file_name))
        except UnexpectedTokenException as e:
            print "Error in file {0}:\n".format(file_name)
            print e
            #return
        except TokenMismatchException as e:
            print "Error in file {0}:\n".format(file_name)
            print e
            #return

    def __flatten_queue(self):
        """
        Flattens list of parsed files so that each nested object is treated as a separate entity
        :return:
        """
        flattened = 0

        while len(self.cdm_entities) != flattened:
            for i in range(flattened, len(self.cdm_entities)):
                cdm_entity = self.cdm_entities[i]
                #print cdm_entity.value.v
                for key in cdm_entity.value.v:
                    if cdm_entity.value.v[key].predicted_type is JSONValueType.object:
                        self.cdm_entities.append(CDMEntity(copy.deepcopy(cdm_entity.value.v[key]), cdm_entity.file_name))
                        self.cdm_entities[i].value.v[key].v = {}
                    elif cdm_entity.value.v[key].predicted_type is JSONValueType.array:
                        if type(cdm_entity.value.v[key].v[0]) is dict:
                            self.cdm_entities[i].value.v[key].v = [cdm_entity.value.v[key].v[0]]
                            #todo spaghetti below. and above
                            self.cdm_entities.append(CDMEntity(JSONValueModel(key, cdm_entity.value.v[key].v[0]), cdm_entity.file_name))

                flattened += 1


class CDMEntity():
    def __init__(self, value, file_name, **kwargs):
        self.value = value
        self.file_name = file_name

    def generate(self, output_dir=None, **kwargs):
        predict_references = kwargs.get("predict_references", False)
        output = u"{\n"
        dictionary = self.value.v
        key_count = len(dictionary.keys())
        i = 0
        output += u"\t\"{0}\":\"{1}\",\n".format(ORIGIN_KEY, self.file_name)
        for key in dictionary:
            name = key
            value = u""
            if predict_references and dictionary[key].predicted_type in referencing_types:
                for reference in dictionary[key].predicted_references:
                    value += u":{0}".format(reference)

                if dictionary[key].predicted_type is JSONValueType.array:
                    value = JSONValueType.get_conf_str_for_val_type(dictionary[key].v[0], value)
                    value = u"[{0}]".format(value)
                else:
                    value = JSONValueType.get_conf_str_for_ref_type(dictionary[key].predicted_type, value)
            else:
                value = JSONValueType.get_str_for_type(dictionary[key].predicted_type)

            output += u"\t\"{0}\": \"{1}\"".format(name, value)
            if i < key_count - 1:
                output += u",\n"
            else:
                output += u"\n"
            i += 1

        output += u"}"

        if output_dir is None:
            print output
        else:
            if not output_dir.endswith("/"):
                output_dir += "/"
            with open(output_dir + self.value.name + ".json", "w") as text_file:
                text_file.write(output)


class DataExampleException(Exception):
    pass


if __name__ == "__main__":
    generator = CDMGenerator("/Users/jzaczek/Documents/Projekty/WEiTI/TKOM/json_examples",
                             "/Users/jzaczek/Documents/Projekty/WEiTI/TKOM/json_configs",
                             predict_references=False)
    generator.generate()