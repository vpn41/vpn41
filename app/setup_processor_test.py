import pytest
from unittest.mock import patch, create_autospec, mock_open

from setup_processor import SetupProcessor, KEYS_FILE_NAME, KEYS_BASE_DIR, SubprocessError
from test_globals import *

from asyncio.subprocess import PIPE, Process
import os.path as osp


@pytest.fixture
def sut():
    return SetupProcessor(app_dir=APP_DIR,
                          ip_address=IP_ADDRESS,
                          ssh_user=SSH_USER,
                          ssh_password=SSH_PASSWORD,
                          first_setup=True,
                          download_keys=True,
                          platform=PLATFORM)


@pytest.fixture
def sut_not_first_time():
    return SetupProcessor(app_dir=APP_DIR,
                          ip_address=IP_ADDRESS,
                          ssh_user=SSH_USER,
                          ssh_password=SSH_PASSWORD,
                          first_setup=False,
                          download_keys=False,
                          platform=PLATFORM)


RETURN_CODE = 0
SETUP_FUNC_RV = 'from stdout', 'from stderr', RETURN_CODE

@pytest.fixture
def create_subprocess_shell_mock():
    patcher = patch('asyncio.create_subprocess_shell')
    m = patcher.start()
    process_mock = create_autospec(Process, spec_set=True, instance=True)
    process_mock.communicate.return_value = b'from stdout', b'from stderr'
    process_mock.returncode = RETURN_CODE
    m.return_value = process_mock
    yield m
    patcher.stop()


@pytest.fixture
def funcs_mock(sut):
    class F:
        pass

    with patch.object(sut, '_scratch_setup') as scratch_setup_mock, \
        patch.object(sut, '_server_setup') as server_setup_mock, \
        patch.object(sut, '_client_setup') as client_setup_mock, \
        patch.object(sut, '_read_keys_file') as read_keys_file_mock:

        scratch_setup_mock.return_value = SETUP_FUNC_RV
        server_setup_mock.return_value = SETUP_FUNC_RV
        client_setup_mock.return_value = SETUP_FUNC_RV

        F.scratch_setup_mock = scratch_setup_mock
        F.server_setup_mock = server_setup_mock
        F.client_setup_mock = client_setup_mock
        F.read_keys_file_mock = read_keys_file_mock
        yield F


@pytest.mark.asyncio
async def test_run_must_handle_exceptions_properly(sut):
    with patch.object(sut, '_scratch_setup') as scratch_setup_mock:

        scratch_setup_mock.side_effect = RuntimeError

        assert not sut.is_completed()
        assert not sut.is_ok()

        with pytest.raises(RuntimeError):
            await sut.run()

        assert sut.is_completed()
        assert not sut.is_ok()


@pytest.mark.asyncio
async def test_run_in_first_time_setup_calls_scratch_server_client_setups(sut, funcs_mock):
    scratch_setup_mock = funcs_mock.scratch_setup_mock
    server_setup_mock = funcs_mock.server_setup_mock
    client_setup_mock = funcs_mock.client_setup_mock
    read_keys_file_mock = funcs_mock.read_keys_file_mock

    data = 'file data'
    read_keys_file_mock.return_value = data

    assert not sut.is_completed()
    assert not sut.is_ok()
    assert sut.keys_file_content() == None

    assert await sut.run() == [SETUP_FUNC_RV, SETUP_FUNC_RV, SETUP_FUNC_RV]

    assert sut.keys_file_content() == data
    assert sut.is_completed()
    assert sut.is_ok()
    scratch_setup_mock.assert_called_with()
    server_setup_mock.assert_called_with()
    client_setup_mock.assert_called_with()
    read_keys_file_mock.assert_called_with()


@pytest.mark.asyncio
async def test_run_must_raise_subprocess_error_if_subprocess_failed(sut, funcs_mock):
    scratch_setup_mock = funcs_mock.scratch_setup_mock
    server_setup_mock = funcs_mock.server_setup_mock
    client_setup_mock = funcs_mock.client_setup_mock
    read_keys_file_mock = funcs_mock.read_keys_file_mock

    client_setup_mock.return_value = *SETUP_FUNC_RV[0:2], 1

    with pytest.raises(SubprocessError) as exc_info:
        await sut.run()

    scratch_setup_mock.assert_called_with()
    server_setup_mock.assert_called_with()
    client_setup_mock.assert_called_with()
    read_keys_file_mock.assert_not_called()


@pytest.mark.asyncio
async def test_run_in_not_first_time_setup_calls_only_client_setup(sut_not_first_time):
    sut = sut_not_first_time
    data = 'file data'
    with patch.object(sut, '_scratch_setup') as scratch_setup_mock, \
         patch.object(sut, '_server_setup') as server_setup_mock, \
         patch.object(sut, '_client_setup') as client_setup_mock, \
         patch.object(sut, '_read_keys_file') as read_keys_file_mock:

        client_setup_mock.return_value = SETUP_FUNC_RV
        read_keys_file_mock.return_value = data
        await sut.run()

        assert sut.keys_file_content() == None
        scratch_setup_mock.assert_not_called()
        server_setup_mock.assert_not_called()
        client_setup_mock.assert_called_with()
        read_keys_file_mock.assert_not_called()


@pytest.mark.asyncio
async def test_scratch_setup_must_call_create_subprocess_shell_properly(sut, create_subprocess_shell_mock):
    assert await sut._scratch_setup() == SETUP_FUNC_RV
    create_subprocess_shell_mock.assert_awaited_with(
        osp.join(APP_DIR, 'vpn-setup/local/scratch-setup.sh') + f" '{IP_ADDRESS}' {SSH_PASSWORD}",
        stdout=PIPE, stderr=PIPE)

    process_mock = create_subprocess_shell_mock.return_value
    process_mock.communicate.assert_awaited_with()


@pytest.mark.asyncio
async def test_server_setup_must_call_create_subprocess_shell_properly(sut, create_subprocess_shell_mock):
    assert await sut._server_setup() == SETUP_FUNC_RV
    create_subprocess_shell_mock.assert_awaited_with(
        osp.join(APP_DIR, 'vpn-setup/local/server-setup.sh') + f" '{IP_ADDRESS}' {SSH_PASSWORD}",
        stdout=PIPE, stderr=PIPE)

    comm = create_subprocess_shell_mock.return_value.communicate
    comm.assert_awaited_with()


@pytest.mark.asyncio
async def test_client_setup_must_call_create_subprocess_shell_properly(sut, create_subprocess_shell_mock):
    assert await sut._client_setup() == SETUP_FUNC_RV
    create_subprocess_shell_mock.assert_awaited_with(
        osp.join(APP_DIR, 'vpn-setup/local/client-setup.sh') + f" '{IP_ADDRESS}' {SSH_PASSWORD} '{True}' '{PLATFORM}'",
        stdout=PIPE, stderr=PIPE)

    comm = create_subprocess_shell_mock.return_value.communicate
    comm.assert_awaited_with()


def test_read_keys_file_must_read_the_file(sut):
    data = 'Splash data from file'
    fn = osp.join(KEYS_BASE_DIR, IP_ADDRESS, 'root', KEYS_FILE_NAME)
    with patch('builtins.open', mock_open(read_data=data)) as open_mock, patch('os.remove') as os_remove_mock:
        assert sut._read_keys_file() == data
        open_mock.assert_called_with(fn, 'rb')
        os_remove_mock.assert_called_with(fn)
