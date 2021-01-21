import string
import random

def is_get(method):
    return method == 'GET'


def is_post(method):
    return method == 'POST'


def is_delete(method):
    return method == 'DELETE'


def make_key(n=32):
    return ''.join(random.choice(string.hexdigits.lower()) for _ in range(n))

