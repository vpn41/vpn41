import logging
import os.path


class NotDirectoryError(RuntimeError):
    pass


def ensure_log_invariant(log_directory):
    os.makedirs(log_directory, exist_ok=True)

    if not os.path.isdir(log_directory):
        raise NotDirectoryError(f'The path is not a directory [{log_directory}]')


class Logger:
    def __init__(self, log_directory=None):
        if log_directory is not None:
            log_directory = os.path.abspath(log_directory)
            ensure_log_invariant(log_directory)
            logging.basicConfig(filename=os.path.join(log_directory, 'vpn41.log'), format='%(name)s')

        self.__logger = logging.getLogger('app')

    def debug(self, message, *args, **kwargs):
        self.__logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.__logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.__logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.__logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.__logger.critical(message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        self.__logger.exception(message, *args, **kwargs)

