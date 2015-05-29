__author__ = 'jzaczek'
from unittest import TestCase
from io import StringIO
from json2code.scanner import Scanner, TokenMismatchException
from json2code.tokens import Token, TokenType


class ScannerReadTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_lbrace(self):
        io = StringIO()
        io.write(u"{")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.lbrace)

        self.assertEqual(scanner.token, Token(TokenType.lbrace, u"{"))

    def test_read_rbrace(self):
        io = StringIO()
        io.write(u"}")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.rbrace)

        self.assertEqual(scanner.token, Token(TokenType.rbrace, u"}"))

    def test_read_lsquare(self):
        io = StringIO()
        io.write(u"[")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.lsquare)

        self.assertEqual(scanner.token, Token(TokenType.lsquare, u"["))

    def test_read_rsquare(self):
        io = StringIO()
        io.write(u"]")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.rsquare)

        self.assertEqual(scanner.token, Token(TokenType.rsquare, u"]"))

    def test_read_comma(self):
        io = StringIO()
        io.write(u",")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.comma)

        self.assertEqual(scanner.token, Token(TokenType.comma, u","))

    def test_read_colon(self):
        io = StringIO()
        io.write(u":")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.colon)

        self.assertEqual(scanner.token, Token(TokenType.colon, u":"))

    def test_read_null(self):
        io = StringIO()
        io.write(u"null")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.null)

        self.assertEqual(scanner.token, Token(TokenType.null, u"null"))

    def test_read_true(self):
        io = StringIO()
        io.write(u"true")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.true)

        self.assertEqual(scanner.token, Token(TokenType.true, u"true"))

    def test_read_false(self):
        io = StringIO()
        io.write(u"false")
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.false)

        self.assertEqual(scanner.token, Token(TokenType.false, u"false"))

    def test_read_string(self):
        io = StringIO()
        unicode_str = u"\" \\\\ \\\" \\/ \\b \\n \\t \\r \\f 123 abc \\u32ef\""
        io.write(unicode_str)
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.string)

        self.assertEqual(scanner.token, Token(TokenType.string, unicode_str))

    def test_read_integer(self):
        io = StringIO()
        unicode_str = u"1342"
        io.write(unicode_str)
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.number)

        self.assertEqual(scanner.token, Token(TokenType.number, unicode_str))

    def test_read_integer_with_fraction(self):
        io = StringIO()
        unicode_str = u"1342.324"
        io.write(unicode_str)
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.number)

        self.assertEqual(scanner.token, Token(TokenType.number, unicode_str))

    def test_read_integer_with_exponent(self):
        io = StringIO()
        unicode_str = u"1342e123"
        io.write(unicode_str)
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.number)

        self.assertEqual(scanner.token, Token(TokenType.number, unicode_str))

    def test_read_integer_with_fraction_and_exponent(self):
        io = StringIO()
        unicode_str = u"1142.234e12"
        io.write(unicode_str)
        scanner = Scanner()
        scanner.file_input = io
        scanner.advance()
        scanner.require_token(TokenType.number)

        self.assertEqual(scanner.token, Token(TokenType.number, unicode_str))

    def test_read_unterminated_string(self):
        io = StringIO()
        unicode_str = u"\"string \\uc223 "
        io.write(unicode_str)
        scanner = Scanner()
        scanner.file_input = io
        with self.assertRaises(TokenMismatchException):
            scanner.advance()

    def test_read_single_backslash(self):
        io = StringIO()
        unicode_str = u"\"string \e e \""
        io.write(unicode_str)
        scanner = Scanner()
        scanner.file_input = io
        with self.assertRaises(TokenMismatchException):
            scanner.advance()