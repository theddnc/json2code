from io import StringIO
from json2code.json import JSONValueType
from json2code.scanner import UnexpectedTokenException, TokenMismatchException

__author__ = 'jzaczek'
from unittest import TestCase
from json2code.parser import Parser, MalformedArrayException, MalformedObjectException


class ParserTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_simple_object(self):
        io = StringIO()
        unicode_str = u"{\"mati\":123.30e2,\"tadzik\":{\"grzes\":true}}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        parser.parse_json()
        result = parser.result

        self.assertEqual(result[u"mati"].v, 12330.0)
        self.assertEqual(result[u"tadzik"].v["grzes"].v, True)

    def test_parse_complex_object(self):
        io = StringIO()
        unicode_str = u"{\"object_id\":123,\"float_v\":1.65e-2,\"array_v\":[null,false,true,10],\"string_v\":\"string!\"}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        parser.parse_json()
        result = parser.result
        self.assertEqual(result[u"object_id"].v, 123)
        self.assertEqual(result[u"object_id"].predicted_type, JSONValueType.id)
        self.assertEqual(result[u"object_id"].predicted_reference, u"object")
        self.assertEqual(result[u"float_v"].v, 0.0165)
        self.assertEqual(result[u"array_v"].v[0], None)
        self.assertEqual(result[u"array_v"].v[1], False)
        self.assertEqual(result[u"array_v"].v[2], True)
        self.assertEqual(result[u"array_v"].v[3], 10)
        self.assertEqual(result[u"string_v"].v, u"string!")

    def test_parse_malformed_array(self):
        io = StringIO()
        unicode_str = u"{\"array\":[1, 2, 3, 4,]}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(MalformedArrayException):
            parser.parse_json()

    def test_parse_malformed_object(self):
        io = StringIO()
        unicode_str = u"{\"array\":[1, 2, 3, 4], \"another_member\": 34,}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(MalformedObjectException):
            parser.parse_json()

    def test_unexpected_token_in_array(self):
        io = StringIO()
        unicode_str = u"{\"array\":[1, {2, 3, 4]}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(UnexpectedTokenException):
            parser.parse_json()

    def test_unexpected_token_in_object(self):
        io = StringIO()
        unicode_str = u"{\"array\":[1, 2, 3, 4], \"obj\": 23, []}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(UnexpectedTokenException):
            parser.parse_json()

    def test_unexpected_token_in_pair(self):
        io = StringIO()
        unicode_str = u"{\"mama\": \"grazyna\"\"gra\",\"tata\":\"bedzie blad\"}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(UnexpectedTokenException):
            parser.parse_json()

    def test_token_mismatch_in_value(self):
        io = StringIO()
        unicode_str = u"{\"array\":[1, 2, 3, 4], \"obj\": error}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(TokenMismatchException):
            parser.parse_json()

    def test_token_mismatch_in_pair(self):
        io = StringIO()
        unicode_str = u"{\"array\":[1, 2, 3, 4], \"obj\"\": 23, []}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(TokenMismatchException):
            parser.parse_json()

    def test_this_is_not_json_sorry(self):
        io = StringIO()
        unicode_str = u"I'm sorry"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        with self.assertRaises(TokenMismatchException):
            parser.parse_json()

    def test_parse_date(self):
        io = StringIO()
        unicode_str = u"{\"date\":\"2008-09-03T20:56:35.450686Z\"}"
        io.write(unicode_str)
        parser = Parser()
        parser.scanner.file_input = io

        parser.parse_json()
        result = parser.result
        self.assertEqual(result[u"date"].predicted_type, JSONValueType.date)