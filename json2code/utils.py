import random
import string

__author__ = 'jzaczek'


def get_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def to_camel_case(snake_str, **kwargs):
    capital = kwargs.get("capital", False)
    components = snake_str.split('_')
    if not capital:
        return components[0] + "".join(x.title() for x in components[1:])
    else:
        return "".join(x.title() for x in components)