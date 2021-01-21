import ipaddress
import shlex

MAX_PASSWD_LEN = 64

def ip_address(ip_addr):
    ipaddress.ip_address(ip_addr)

    if ip_addr == '127.0.0.1':
        raise ValueError('Localhost is invalid address')

    return ip_addr


def user_name(user):
    if user != 'root':
        raise ValueError('Only root allowed for now')

    return user


def password(passwd):
    if len(passwd) > MAX_PASSWD_LEN:
        raise ValueError('Password length exceeding')

    return shlex.quote(passwd)


def boolean(value):
    return bool(value)


def platform(value):
    if value not in ('linux', 'none'):
        raise ValueError('Invalid platform specified')

    return value
