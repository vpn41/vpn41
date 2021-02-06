import json

import flask
from flask import url_for, request, session, redirect, render_template
from werkzeug.exceptions import MethodNotAllowed, NotFound, BadRequest, NotAcceptable

import settings
import validator as v
from setup_processors_pool import AlreadyInProgressError
from aux_stuff import *


class MainRequestHandler:
    def __init__(self, setup_controller, logger):
        self.__setup_controller = setup_controller
        self.__logger = logger


    def before_request(self):
        session.permanent = True

        if 'key' not in session:
            session['key'] = make_key()

        if request.view_args and 'locale' in request.view_args:
            locale = request.view_args['locale']
            if locale in settings.LOCALES:
                session['locale'] = locale
                request.view_args.pop('locale')
            else:
                return redirect(url_for('index', locale=settings.DEFAULT_LOCALE))


    def get_locale(self):
        locale = session.get('locale')
        if locale is not None:
            return locale

        return request.accept_languages.best_match([settings.EN_LOCALE]) or settings.DEFAULT_LOCALE


    def root(self):
        return redirect(url_for('index', locale=self.get_locale()))


    def index(self):
        cur_locale = str(self.get_locale())
        return flask.render_template("home.html",
                               locale=cur_locale.capitalize(),
                               title="Setup Your Own VPN Server | Vpn4.One",
                               status=json.dumps(self.__status()))


    def setup(self):
        try:
            ip_addr = v.ip_address(request.form["ip-address"])
            ssh_user = v.user_name(request.form["ssh-user"])
            ssh_password = v.password(request.form["ssh-password"])
            first_setup = v.boolean(request.form.get("first-setup", False))
            download_keys = v.boolean(request.form.get("download-keys", False))
            platform = v.platform(request.form.get('platform', 'none'))
        except ValueError:
            raise BadRequest()

        key = session['key']

        try:
            self.__setup_controller.setup(key=key, ip_address=ip_addr, ssh_user=ssh_user, ssh_password=ssh_password,
                                          first_setup=first_setup, download_keys=download_keys, platform=platform)
        except AlreadyInProgressError:
            self.__logger.info(f'[{key}]: Setup is already in progress')
            raise NotAcceptable()

        return '', 202


    def status(self):
        if is_get(request.method):
            return self.__status(), 200
        elif is_delete(request.method):
            self.__setup_controller.clear_status(key=session['key'])
            return '', 204
        else:
            raise MethodNotAllowed()


    def keys_file(self):
        content = self.__setup_controller.keys_file_content(key=session['key'])
        if content is None:
            raise NotFound()

        return (content,
               [
                    ('Content-Disposition', f'attachment; filename="{settings.KEYS_FILE_NAME}"'),
                    ('Content-Description', 'File Transfer'),
                    ('Content-Type', 'application/zip, application/octet-stream'),
                    ('Content-Length', f'{len(content)}')
               ])


    def __status(self):
        return self.__setup_controller.status(key=session['key'])

