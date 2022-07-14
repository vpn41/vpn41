import pytest
from unittest.mock import create_autospec, ANY, patch

from app import create_flask_app
from main_req_handler import MainRequestHandler
from aux_stuff import make_key
from setup_controller import SetupController
from setup_processors_pool import AlreadyInProgressError
from logger import Logger
import settings

from flask import session, request, make_response
import json
import re

from test_globals import *

STATUS_PAYLOAD = dict(status='undefined')
KEYS_FILE_CONTENT = b'keys file content'


@pytest.fixture
def setup_controller_mock():
    mock = create_autospec(SetupController, spec_set=True, instance=True)
    mock.status.return_value = STATUS_PAYLOAD
    mock.keys_file_content.return_value = KEYS_FILE_CONTENT
    return mock


@pytest.fixture
def logger_mock():
    return create_autospec(spec=Logger, spec_set=True, instance=True)


@pytest.fixture
def sut(setup_controller_mock, logger_mock):
    return MainRequestHandler(setup_controller=setup_controller_mock, logger=logger_mock)


@pytest.fixture
def flask_client(sut):
    app = create_flask_app(sut)
    context = app.app_context()
    context.push()
    client = app.test_client()

    with client:
        yield client

    context.pop()


@pytest.fixture
def input_data():
    return {
        'ip-address': IP_ADDRESS,
        'ssh-user': SSH_USER,
        'ssh-password': SSH_PASSWORD,
        'first-setup': True,
        'download-keys': True
    }


def test_make_key():
    r = make_key(32)
    assert isinstance(r, str)
    assert re.match('^[0-9a-f]{32}$', r)


def test_before_request(flask_client):
    flask_client.get('/en/')
    assert 'key' in session
    assert 'locale' in session and session['locale'] == 'en'
    assert session.permanent
    assert 'locale' not in request.view_args


@pytest.mark.parametrize('data, expected', [({'ip-address': IP_ADDRESS,
                                              'ssh-user': SSH_USER,
                                              'ssh-password': SSH_PASSWORD,
                                              'first-setup': True,
                                              'download-keys': True,
                                              'platform': PLATFORM},
                                             {'ip_address': IP_ADDRESS,
                                              'ssh_user': SSH_USER,
                                              'ssh_password': SSH_PASSWORD,
                                              'first_setup': True,
                                              'download_keys': True,
                                              'platform': PLATFORM}),
                                            ({'ip-address': IP_ADDRESS,
                                              'ssh-user': SSH_USER,
                                              'ssh-password': SSH_PASSWORD},
                                             {'ip_address': IP_ADDRESS,
                                              'ssh_user': SSH_USER,
                                              'ssh_password': SSH_PASSWORD,
                                              'first_setup': False,
                                              'download_keys': False,
                                              'platform': 'none'})])
def test_setup_must_return_no_content_success_if_everything_was_ok(flask_client, setup_controller_mock, data, expected):
    rv = flask_client.post('/setup/', data=data)

    assert rv.status_code == 202 and rv.data == b''
    key = session['key']
    setup_controller_mock.setup.assert_called_with(key=key, **expected)


@pytest.mark.parametrize('data', [{'ip-address': 'asdf',
                                  'ssh-user': SSH_USER,
                                  'ssh-password': SSH_PASSWORD,
                                  'first-setup': True,
                                  'download-keys': True},
                                {'ip-address': IP_ADDRESS,
                                  'ssh-user': 'asdf',
                                  'ssh-password': SSH_PASSWORD}])
def test_setup_must_return_bad_req_if_invalid_args_provided(flask_client, setup_controller_mock, data):
    rv = flask_client.post('/setup/', data=data)

    assert rv.status_code == 400
    setup_controller_mock.setup.assert_not_called()


def test_setup_must_return_not_acceptable_if_setup_already_in_progress(flask_client, setup_controller_mock, input_data):
    setup_controller_mock.setup.side_effect = AlreadyInProgressError
    rv = flask_client.post('/setup/', data=input_data)
    assert rv.status_code == 406


def test_status_get(flask_client, setup_controller_mock):
    rv = flask_client.get('/status/')
    assert rv.status_code == 200 and json.loads(rv.data) == STATUS_PAYLOAD
    key = session['key']
    setup_controller_mock.status.assert_called_with(key=key)


def test_status_delete(flask_client, setup_controller_mock):
    rv = flask_client.delete('/status/')
    assert rv.status_code == 204 and rv.data == b''
    key = session['key']
    setup_controller_mock.clear_status.assert_called_with(key=key)


def test_keys_file_success(flask_client, setup_controller_mock):
    rv = flask_client.get('/keys/')
    assert rv.data == KEYS_FILE_CONTENT
    assert rv.headers['Content-Disposition'] == f'attachment; filename="{settings.KEYS_FILE_NAME}"'
    assert rv.headers['Content-Description'] == 'File Transfer'
    assert rv.headers['Content-Type'] == 'application/zip, application/octet-stream'
    assert rv.headers['Content-Length'] == f'{len(KEYS_FILE_CONTENT)}'
    setup_controller_mock.keys_file_content.assert_called_with(key=session['key'])


def test_keys_file_must_return_not_found_if_no_keys_available(flask_client, setup_controller_mock):
    setup_controller_mock.keys_file_content.return_value = None
    rv = flask_client.get('/keys/')
    assert rv.status_code == 404
    assert 'Content-Disposition' not in rv.headers
    setup_controller_mock.keys_file_content.assert_called_with(key=session['key'])


@pytest.mark.parametrize('path', ['/', '/asdf/', '/fr/'])
def test_root_and_locale_get_must_for_now_always_redirect_to_en_locale(flask_client, path):
    rv = flask_client.get(path)
    assert rv.status_code == 302
    assert rv.headers['location'] == '/en/'


def test_index_get_must_setup_en_locale(flask_client):
    with patch('flask.render_template') as render_template_mock:
        render_template_mock.return_value = make_response('')
        rv = flask_client.get('/en/')

    assert rv.status_code == 200
    assert session['locale'] == settings.EN_LOCALE
    render_template_mock.assert_called_with('home.html',
                                            locale=settings.EN_LOCALE.capitalize(),
                                            title="Setup Your Own VPN Server | Vpn4.One",
                                            status=ANY)
