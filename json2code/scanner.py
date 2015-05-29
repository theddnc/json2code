import string

__author__ = 'jzaczek'
import io
from json2code.tokens import TokenType, Token
import inspect


HEX_CHARS = u"abcdef01234567890"
ESCAPED_CHARS = u"\ \"/bfnrt"


class Scanner:
    token = None
    current_byte = 0
    scanned_byte = 0

    # todo: kwargs instead of args?
    def __init__(self, file_name=None):
        if file_name is not None:
            self.file_input = io.open(file_name, encoding='utf-8')
        else:
            self.file_input = None

    def advance(self):
        # try parsing each token
        self.file_input.seek(self.scanned_byte)
        self.__skip_whitespace()
        self.scanned_byte = self.file_input.tell()
        self.current_byte = self.scanned_byte
        member_list = inspect.getmembers(self, predicate=inspect.ismethod)
        for (member_name, member_value) in member_list:
            if member_name.startswith("_read"):
                try:
                    member_value()
                except TokenMismatchException:
                    pass
                else:
                    #print "Current byte: {0}\t Scanned byte: {1}".format(self.current_byte, self.scanned_byte)
                    return

        self.file_input.seek(self.scanned_byte)
        value = self.file_input.readline()
        raise TokenMismatchException("Unable to parse value: {0}.".format(value))

    def require_token(self, token_type):
        if self.token.type != token_type:
            raise UnexpectedTokenException("Token with type: {0} and value {1} was unexpected. Expecting: {2}".
                                           format(self.token.type, self.token.value, token_type))
        else:
            #print "Forwarding from scanned: {0} to current: {1}".format(self.scanned_byte, self.current_byte)
            self.scanned_byte = self.current_byte

    def peek(self, length):
        self.__skip_whitespace()

        self.file_input.seek(self.current_byte)
        value = self.file_input.read(length)
        self.file_input.seek(self.current_byte)

        return value

    # TOKEN DEFINITIONS BELOW -----------------------------------------------------------------------------------------

    def _read_lbrace(self):
        token = Token(TokenType.lbrace, u'')
        self.__read_one_char(token, u'{')

    def _read_rbrace(self):
        token = Token(TokenType.rbrace, u'')
        self.__read_one_char(token, u'}')

    def _read_lsquare(self):
        token = Token(TokenType.lsquare, u'')
        self.__read_one_char(token, u'[')

    def _read_rsquare(self):
        token = Token(TokenType.rsquare, u'')
        self.__read_one_char(token, u']')

    def _read_comma(self):
        token = Token(TokenType.comma, u'')
        self.__read_one_char(token, u',')

    def _read_colon(self):
        token = Token(TokenType.colon, u'')
        self.__read_one_char(token, u':')

    def _read_string(self):
        self.file_input.seek(self.current_byte)
        opening_quote = self.file_input.read(1)
        if opening_quote != u'"':
            raise TokenMismatchException("No opening quote, got: {0}".format(opening_quote))

        # iterate over characters until finding the closing quotation mark
        # string is saved in value
        value = opening_quote
        current_pos = self.file_input.tell()
        finished = False
        while not finished:
            try:
                self.file_input.seek(current_pos)
                char = self.__read_escaped_unicode_character()
            except EscapedUnicodeException:
                self.file_input.seek(current_pos)
                char = self.__read_unicode_character()

            current_pos = self.file_input.tell()
            value += char
            if char == u'"':
                finished = True

            if char == u"" or char is None:
                raise TokenMismatchException("No closing quote, got value: {0}.".format(value))

        self.current_byte = current_pos
        self.token = Token(TokenType.string, value)

    def _read_number(self):
        self.file_input.seek(self.current_byte)

        try:
            integer_value = self.__read_integer()
            current_pos = self.file_input.tell()
        except NaNException:
            raise TokenMismatchException("No integer part found")

        # we've got an integer, let's try finding a fraction
        try:
            fraction_value = self.__read_fraction()
            current_pos = self.file_input.tell()
        except NaNException as e:
            # oops, no fraction, maybe an exponent? - let's rewind
            self.file_input.seek(current_pos)

            try:
                exponent_value = self.__read_exponent()
                current_pos = self.file_input.tell()
            except NaNException as e:
                # found nothing more, this is an integer!
                self.current_byte = current_pos
                self.token = Token(TokenType.number, integer_value)
                return

            # got a number with integer and exponent components (e.g. 2e10)
            self.current_byte = current_pos
            self.token = Token(TokenType.number, integer_value+exponent_value)
            return

        # found a fraction, how about exponent?
        try:
            exponent_value = self.__read_exponent()
            current_pos = self.file_input.tell()
        except NaNException as e:
            # oops, no exponent there, we've got ourselves a fraction (e.g. 20.2321)
            self.current_byte = current_pos
            self.token = Token(TokenType.number, integer_value+fraction_value)
            return

        # found everything! we've got ourselves something like: 0.23e10
        self.current_byte = current_pos
        self.token = Token(TokenType.number, integer_value+fraction_value+exponent_value)

    def _read_true(self):
        token = Token(TokenType.true, u'')
        self.__read_one_word(token, u"true")

    def _read_false(self):
        token = Token(TokenType.false, u'')
        self.__read_one_word(token, u"false")

    def _read_null(self):
        token = Token(TokenType.null, u'')
        self.__read_one_word(token, u"null")

    # HELPER FUNCTIONS BELOW ------------------------------------------------------------------------------------------

    def __read_one_word(self, token, predicted):
        self.file_input.seek(self.current_byte)
        word = self.file_input.read(len(predicted))
        if word != predicted:
            raise TokenMismatchException("Wanted: {0}, got: {1}".format(predicted, word))

        self.current_byte = self.file_input.tell()
        token.value = word
        self.token = token

    def __read_one_char(self, token, predicted):
        self.file_input.seek(self.current_byte)
        char = self.file_input.read(1)
        if char != predicted:
            raise TokenMismatchException("Wanted: {0}, got: {1}".format(predicted, char))

        self.current_byte = self.file_input.tell()
        token.value = char
        self.token = token

    # STRING HELPER FUNCTIONS BELOW

    def __read_escaped_unicode_character(self):
        backslash = self.file_input.read(1)
        if backslash != u"\\":
            raise EscapedUnicodeException("No \ (backslash) at the beginning")

        current_pos = self.file_input.tell()
        try:
            value = self.__read_four_hex_digits()
        except EscapedUnicodeException:
            self.file_input.seek(current_pos)
            char = self.file_input.read(1)
            if ESCAPED_CHARS.find(char.lower()) == -1:
                raise EscapedUnicodeException("Found \ (backslash) but the next char is {0}".format(char))
            value = char

        return backslash+value

    def __read_unicode_character(self):
        char = self.file_input.read(1)
        if char == u"\\":
            raise TokenMismatchException("Found \ (backslash) unexpectedly (with no escaped chars to follow)")

        return char

    def __read_four_hex_digits(self):
        u_char = self.file_input.read(1)
        if u_char != u'u':
            raise EscapedUnicodeException("Could not find 'u' as the first char of escaped unicode")
        hex_digit = self.file_input.read(4)
        for char in hex_digit:
            if HEX_CHARS.find(char.lower()) == -1:
                raise EscapedUnicodeException("One of the four char is not hex digit, got: {0}".format(hex_digit))

        return u_char+hex_digit

    # NUMBER HELPER FUNCTIONS BELOW

    def __read_integer(self):
        value = u""
        char = self.file_input.read(1)

        if not (char.isnumeric() or char == u"-"):
            raise NaNException("First char is neither a digit nor a minus (-) sign, got: {0}.".format(char))

        if char == u"-":
            value += char

        if char == u"0":
            value += char
        else:
            curr_pos = self.file_input.tell()
            while char.isnumeric():
                value += char
                curr_pos = self.file_input.tell()
                char = self.file_input.read(1)

            self.file_input.seek(curr_pos)

        return value

    def __read_fraction(self):
        value = u""
        dot = self.file_input.read(1)
        if dot != u".":
            raise NaNException("First char is not a '.' (dot), got: {0}.".format(dot))

        value += dot

        curr_pos = self.file_input.tell()
        char = self.file_input.read(1)

        while char.isnumeric():
            value += char
            curr_pos = self.file_input.tell()
            char = self.file_input.read(1)

        self.file_input.seek(curr_pos)

        return value

    def __read_exponent(self):
        value = u""
        char = self.file_input.read(1)

        if char != u"e" and char != u"E":
            raise NaNException("First char is neither 'e' nor 'E', got: {0}.".format(char))
        value += char

        char = self.file_input.read(1)

        if char == u"+" or char == u"-":
            value += char
            char = self.file_input.read(1)

        if not char.isnumeric():
            raise NaNException("Following chars are not digits, got: {0}.".format(char))

        curr_pos = self.file_input.tell()
        while char.isnumeric():
            value += char
            curr_pos = self.file_input.tell()
            char = self.file_input.read(1)

        self.file_input.seek(curr_pos)

        return value

    # OTHER HELPER FUNCTIONS BELOW

    def __skip_whitespace(self):
        curr_pos = self.file_input.tell()
        char = self.file_input.read(1)
        while char in string.whitespace:
            curr_pos = self.file_input.tell()
            char = self.file_input.read(1)
            continue

        self.file_input.seek(curr_pos)


class TokenMismatchException(Exception):
    pass


class EscapedUnicodeException(Exception):
    pass


class UnexpectedTokenException(Exception):
    pass


class NaNException(Exception):
    pass