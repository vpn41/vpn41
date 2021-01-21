import pytest
from unittest.mock import create_autospec, ANY, patch

from app import create_flask_app
from main_req_handler import MainRequestHandler
from aux_stuff import make_key
from setup_controller import SetupController
from setup_processors_pool import AlreadyInProgressError
from logger import Logger
import settings

import flask
from flask import session, request, make_response
import json
import re

from test_globals import *

STATUS_PAYLOAD = dict(status='undefined')
KEYS_FILE_CONTENT = b'keys file content'

@pytest.fixture
def f():
    class F:
        setup_controller_mock = create_autospec(SetupController, spec_set=True, instance=True)
        setup_controller_mock.status.return_value = STATUS_PAYLOAD
        setup_controller_mock.keys_file_content.return_value = KEYS_FILE_CONTENT
        logger_mock = create_autospec(spec=Logger, spec_set=True, instance=True)

        sut = MainRequestHandler(setup_controller=setup_controller_mock, logger=logger_mock)
        app = create_flask_app(sut)
        context = app.app_context()
        context.push()
        client = app.test_client()

        data = {
            'ip-address': IP_ADDRESS,
            'ssh-user': SSH_USER,
            'ssh-password': SSH_PASSWORD,
            'first-setup': True,
            'download-keys': True
        }

    with F.client:
        yield F

    F.context.pop()


def test_make_key(f):
    r = make_key(32)
    assert isinstance(r, str)
    assert re.match('^[0-9a-f]{32}$', r)


def test_before_request(f):
    f.client.get('/en/')
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
def test_setup_must_return_no_content_success_if_everything_was_ok(f, data, expected):
    rv = f.client.post('/setup/', data=data)

    assert rv.status_code == 202 and rv.data == b''
    key = session['key']
    f.setup_controller_mock.setup.assert_called_with(key=key, **expected)


@pytest.mark.parametrize('data', [{'ip-address': 'asdf',
                                  'ssh-user': SSH_USER,
                                  'ssh-password': SSH_PASSWORD,
                                  'first-setup': True,
                                  'download-keys': True},
                                {'ip-address': IP_ADDRESS,
                                  'ssh-user': 'asdf',
                                  'ssh-password': SSH_PASSWORD}])
def test_setup_must_return_bad_req_if_invalid_args_provided(f, data):
    rv = f.client.post('/setup/', data=data)

    assert rv.status_code == 400
    f.setup_controller_mock.setup.assert_not_called()


def test_setup_must_return_not_acceptable_if_setup_already_in_progress(f):
    f.setup_controller_mock.setup.side_effect = AlreadyInProgressError
    rv = f.client.post('/setup/', data=f.data)
    assert rv.status_code == 406


def test_status_get(f):
    rv = f.client.get('/status/')
    assert rv.status_code == 200 and json.loads(rv.data) == STATUS_PAYLOAD
    key = session['key']
    f.setup_controller_mock.status.assert_called_with(key=key)


def test_status_delete(f):
    rv = f.client.delete('/status/')
    assert rv.status_code == 204 and rv.data == b''
    key = session['key']
    f.setup_controller_mock.clear_status.assert_called_with(key=key)


def test_keys_file_success(f):
    rv = f.client.get('/keys/')
    assert rv.data == KEYS_FILE_CONTENT
    assert rv.headers['Content-Disposition'] == f'attachment; filename="{settings.KEYS_FILE_NAME}"'
    assert rv.headers['Content-Description'] == 'File Transfer'
    assert rv.headers['Content-Type'] == 'application/zip, application/octet-stream'
    assert rv.headers['Content-Length'] == f'{len(KEYS_FILE_CONTENT)}'
    f.setup_controller_mock.keys_file_content.assert_called_with(key=session['key'])


def test_keys_file_must_return_not_found_if_no_keys_available(f):
    f.setup_controller_mock.keys_file_content.return_value = None
    rv = f.client.get('/keys/')
    assert rv.status_code == 404
    assert 'Content-Disposition' not in rv.headers
    f.setup_controller_mock.keys_file_content.assert_called_with(key=session['key'])


@pytest.mark.parametrize('path', ['/', '/asdf/', '/fr/'])
def test_root_and_locale_get_must_for_now_always_redirect_to_en_locale(f, path):
    rv = f.client.get(path)
    assert rv.status_code == 302
    assert rv.headers['location'] == 'http://localhost/en/'


def test_index_get_must_setup_en_locale(f):
    with patch('flask.render_template') as render_template_mock:
        render_template_mock.return_value = make_response('')
        rv = f.client.get('/en/')

    assert rv.status_code == 200
    assert session['locale'] == settings.EN_LOCALE
    render_template_mock.assert_called_with('home.html',
                                            locale=settings.EN_LOCALE.capitalize(),
                                            title="Setup Own VPN Server | Vpn4.One",
                                            status=ANY)
