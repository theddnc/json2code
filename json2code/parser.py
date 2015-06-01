from scanner import Scanner, TokenMismatchException, UnexpectedTokenException
from tokens import TokenType
from json_value import JSONValueModel

__author__ = 'jzaczek'


class Parser:
    # todo: think of option kwargs (perhaps fuzzy json parse?)
    def __init__(self, **kwargs):
        """
        :param kwargs:
            simple_value: default True, if set to False uses JSONValueModel
            file_name: name of the file to parse
            io: string io, pass if file_name is None
            predict_references: default False, if true will try to predict links in data model
        :return:
        """
        self.simple_value = kwargs.get("simple_value", True)
        self.predict_references = kwargs.get("predict_references", False)
        file_name = kwargs.get("file_name", None)
        io = kwargs.get("io", None)

        self.parsed_string = u""
        self.result = {}
        self.scanner = Scanner(file_name)
        if file_name is None and io is not None:
            self.scanner.file_input = io

    def parse_json(self):
        """
        parses json loaded by scanner
        raises TokenMismatchException or UnexpectedTokenException
        :return: parsed dictionary of JSONValueModel
        """

        self.result = self.__parse_object()

    def __parse_value(self):
        """
        Parses value, which can be string, number, array, object, null, true, false
        :return: parsed value (list, dict, unicode, int, float, bool, None)
        """
        char = self.scanner.peek(1)

        if char == u'{':
            return self.__parse_object()
        elif char == u'[':
            return self.__parse_array()
        elif char == u'n':
            return self.__parse_null()
        elif char == u't':
            return self.__parse_bool()
        elif char == u'f':
            return self.__parse_bool()
        elif char == u'"':
            return self.__parse_string()
        else:
            return self.__parse_number()

    def __parse_object(self):
        """
        Parses object
        :return: parsed dictionary
        """
        result = {}
        self.__advance_requiring(TokenType.lbrace)
        try:
            result = self.__parse_members()
        except UnexpectedTokenException:
            pass
        self.__advance_requiring(TokenType.rbrace)

        return result

    def __parse_array(self):
        """
        Parses array of values
        :return: parsed list
        """
        result = []
        self.__advance_requiring(TokenType.lsquare)
        try:
            result = self.__parse_elements()
        except UnexpectedTokenException:
            pass
        self.__advance_requiring(TokenType.rsquare)

        return result

    def __parse_members(self):
        """
        Parses members of potential object
        :return: dictionary with members
        """
        result = {}
        while True:
            try:
                name, value = self.__parse_pair()
                if self.simple_value is False:
                    result[name] = JSONValueModel(name, value, predict_references=self.predict_references)
                else:
                    result[name] = value
            except UnexpectedTokenException:
                raise UnexpectedTokenException
            try:
                self.__advance_requiring(TokenType.comma)
                if self.scanner.peek(1) == u'}':
                    raise MalformedObjectException("Malformed object: got comma and rbrace")
            except UnexpectedTokenException:
                return result

    def __parse_pair(self):
        """
        Parses pair of string: value
        :return: name and value
        """
        name = self.__parse_string()
        self.__advance_requiring(TokenType.colon)
        try:
            value = self.__parse_value()
        except TokenMismatchException as e:
            raise e

        return name, value

    def __parse_elements(self):
        """
        Parses elements of potential array
        :return: list filled with elements
        """
        array = []
        while True:
            try:
                array.append(self.__parse_value())
                self.__advance_requiring(TokenType.comma)
                if self.scanner.peek(1) == u']':
                    raise MalformedArrayException("Malformed array: got comma and rsquare instead of value")
            except UnexpectedTokenException:
                return array

    def __parse_string(self):
        self.__advance_requiring(TokenType.string)
        return self.scanner.token.value[1:-1]  # removes enclosing quotes

    def __parse_number(self):
        self.__advance_requiring(TokenType.number)
        try:
            return int(self.scanner.token.value)
        except ValueError:
            pass

        try:
            return float(self.scanner.token.value)
        except ValueError:
            raise TokenMismatchException

    def __parse_bool(self):
        try:
            self.__advance_requiring(TokenType.true)
            return True
        except UnexpectedTokenException:
            pass

        try:
            self.__advance_requiring(TokenType.false)
            return False
        except UnexpectedTokenException as e:
            raise e

    def __parse_null(self):
        try:
            self.__advance_requiring(TokenType.null)
            return None
        except UnexpectedTokenException as e:
            raise e

    def __advance_requiring(self, token_type):
        #print "Requiring: {0}".format(token_type)
        self.scanner.advance()
        self.scanner.require_token(token_type)
        self.parsed_string += self.scanner.token.value
        #print "Got: {0},\tparsed: ({1}).\n".format(token_type, self.parsed_string)


class MalformedArrayException(Exception):
    pass


class MalformedObjectException(Exception):
    pass