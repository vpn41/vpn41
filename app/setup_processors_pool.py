import asyncio

from setup_processor import SetupProcessor, SubprocessError


class AlreadyInProgressError(RuntimeError):
    pass


class SetupProcessorsPool:
    def __init__(self, app_dir, logger, setup_processor_class=SetupProcessor):
        self.__app_dir = app_dir
        self.__logger = logger
        self.__setup_proc_class = setup_processor_class
        self.__pending = dict()
        self.__completed = dict()


    def spawn(self, key, **params):
        if self.is_completed(key):
            self.clear(key)

        if self.is_pending(key):
            raise AlreadyInProgressError(key)

        self.__pending[key] = self.__setup_proc_class(self.__app_dir, **params)


    def pending(self):
        return self.__pending


    def completed(self):
        return self.__completed


    def is_pending(self, key):
        return key in self.__pending


    def is_completed(self, key):
        return key in self.__completed


    def get(self, key):
        try:
            return self.__pending[key]
        except KeyError:
            try:
                return self.__completed[key]
            except KeyError:
                return None


    def clear(self, key):
        try:
            del self.__completed[key]
        except KeyError:
            self.__logger.warning(f'Trying to clear key, but no key found [{key}]')


    async def run_forever(self):
        while True:
            await self.run_once()
            await asyncio.sleep(0.01)


    async def run_once(self):
        pending = self.__pending
        completed = self.__completed
        logger = self.__logger

        procs = tuple(pending.items())
        for key, p in procs:
            try:
                logger.info(f'Starting setup [{key}]...')
                log = await p.run()
                logger.info(f'Setup log\n{log}')
                logger.info(f'Setup completed [{key}]')
            except Exception as e:
                logger.error(f'Error while setup occurred [what: {e}, key: {key}]')
            except SubprocessError as e:
                logger.error(f'Subprocess error returned while setup [what: {e}, key: {key}]')
            finally:
                del pending[key]
                completed[key] = p

