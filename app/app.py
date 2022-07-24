#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os.path

import platform
import signal

import tornado.options
import tornado.ioloop
import tornado.web
import click

from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler

from flask import Flask
from flask_babel import Babel
from flask_mobility import Mobility

import settings
from main_req_handler import MainRequestHandler
from setup_processors_pool import SetupProcessorsPool
from setup_controller import SetupController
from logger import Logger

APP_DIR = os.path.abspath(os.path.dirname(__file__))

def create_flask_app(req_handler):
    flask_app = Flask(__name__, template_folder=resource_path("templates"))
    flask_app.secret_key = settings.SECRET_KEY
    babel = Babel(flask_app)
    Mobility(flask_app)
    flask_app.config['BABEL_DEFAULT_LOCALE'] = settings.DEFAULT_LOCALE
    flask_app.before_request(req_handler.before_request)
    babel.localeselector(req_handler.get_locale)

    flask_app.add_url_rule(rule='/', endpoint='root', view_func=req_handler.root)
    flask_app.add_url_rule(rule='/setup/', endpoint='setup', view_func=req_handler.setup, methods=('POST',))
    flask_app.add_url_rule(rule='/status/', endpoint='status', view_func=req_handler.status, methods=('GET', 'DELETE'))
    flask_app.add_url_rule(rule='/<locale>/', endpoint='index', view_func=req_handler.index)
    flask_app.add_url_rule(rule='/keys/', endpoint='keys', view_func=req_handler.keys_file)

    return flask_app


def app_dir():
    return getattr(sys, '_MEIPASS', APP_DIR)

def resource_path(path):
    return os.path.join(app_dir(), path)


class Application(tornado.web.Application):
    def __init__(self, logger):
        setup_processors_pool = SetupProcessorsPool(app_dir=app_dir(), logger=logger)
        setup_controller = SetupController(setup_processors_pool=setup_processors_pool)
        req_handler = MainRequestHandler(setup_controller=setup_controller, logger=logger)
        self.__setup_processors_pool = setup_processors_pool
        flask_app = create_flask_app(req_handler)
        wsgi_container = WSGIContainer(flask_app)

        handlers = [
            (r".*", FallbackHandler, dict(fallback=wsgi_container)),
        ]
        s = dict(
            static_path=resource_path("static"),
            xsrf_cookies=False,
            debug=True,
        )

        tornado.web.Application.__init__(self, handlers, **s)


    async def setup_processor(self):
        await self.__setup_processors_pool.run_forever()


def setup_signals(logger):
    def signal_handler(signum, frame):
        logger.info("Signal exit")
        sys.exit(0)

    if platform.system() == 'Windows':
        signal.signal(signal.SIGBREAK, signal_handler)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


APP_NAME = 'Vpn4.One'
VERSION = '0.0.3'


@click.command()
@click.option('--address', default='127.0.0.1', help='Address to listen to.', show_default=True)
@click.option('--port', default=8080, help='Port to listen to.', show_default=True)
@click.version_option(version=VERSION, prog_name=APP_NAME)
def cli(address, port):
    try:
        logger = None
        logger = Logger() # log_directory=settings.LOG_DIR
        main(logger, address, port)
    except Exception as e:
        if logger is None:
            print(f'An error occurred on app start [{e}]')
        else:
            logger.error(f'An error occurred on app start [{e}]')


def main(logger, address, port):
    """App entry point"""

    if sys.version_info < (3, 6):
        RuntimeError(f'Incompatible python version: [{sys.version_info}]')

    tornado.options.parse_command_line(args=[])

    setup_signals(logger)

    app = Application(logger=logger)
    app.listen(port, address)
    tornado.ioloop.IOLoop.current().spawn_callback(app.setup_processor)

    logger.info("Started")
    tornado.ioloop.IOLoop.current().start()
    logger.info("Exit")


if __name__ == '__main__':
    cli()