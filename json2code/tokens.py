__author__ = 'jzaczek'

from enum import Enum


class TokenType(Enum):
    lbrace = 1
    rbrace = 2
    lsquare = 3
    rsquare = 4
    comma = 5
    colon = 6
    string = 7
    number = 8
    true = 9
    false = 10
    null = 11


class Token:

    def __init__(self, _type, _value):
        self.type = _type
        self.value = _value

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__