import pytest
from unittest.mock import create_autospec

from setup_controller import SetupController
from setup_processors_pool import SetupProcessorsPool
from setup_processor import SetupProcessor


from test_globals import *

@pytest.fixture
def f():
    class F:
        setup_processors_pool_mock = create_autospec(SetupProcessorsPool, spec_set=True, instance=True)
        sut = SetupController(setup_processors_pool=setup_processors_pool_mock)

    return F


def test_setup_must_call_pool_add_with_correct_params(f):
    f.sut.setup('key', **PARAMS)
    f.setup_processors_pool_mock.spawn.assert_called_with('key', **PARAMS)


def setup_proc_mock(completed_return_value, keys_file_content):
    m = create_autospec(SetupProcessor, spec_set=True, instance=True)
    m.is_completed.return_value = completed_return_value
    m.is_ok.return_value = True
    m.keys_file_content.return_value = keys_file_content
    return m


@pytest.mark.parametrize('get_result, expected_status', [(None, (dict(status='undefined'))),
                                                         (setup_proc_mock(False, None), (dict(status='pending'))),
                                                         (setup_proc_mock(False, 'file content'), (dict(status='pending'))),
                                                         (setup_proc_mock(True, None), (dict(status='completed', ok=True))),
                                                         (setup_proc_mock(True, 'file content'), (dict(status='completed', ok=True, keys_file_url='/keys/')))])
def test_status_must_return_correct_result_depending_on_pool_status(f, get_result, expected_status):
    f.setup_processors_pool_mock.get.return_value = get_result

    assert f.sut.status('key') == expected_status
    f.setup_processors_pool_mock.get.assert_called_with('key')


def test_clear_status_must_call_pool_clear(f):
    f.sut.clear_status('key')
    f.setup_processors_pool_mock.clear.assert_called_with('key')
