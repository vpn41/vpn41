import os.path as osp
import os
from asyncio.subprocess import PIPE
import asyncio

from settings import KEYS_BASE_DIR, KEYS_FILE_NAME


class SubprocessError(RuntimeError):
    pass


class SetupProcessor:
    def __init__(self, app_dir, **params):
        self.__app_dir = app_dir
        self.__ip_addr = params['ip_address']
        self.__ssh_user = params['ssh_user']
        self.__ssh_password = params['ssh_password']
        self.__first_setup = params['first_setup']
        self.__dl_keys = params['download_keys']
        self.__platform = params['platform']

        self.__scratch_setup_porcess = None
        self.__server_setup_process = None
        self.__client_setup_process = None
        self.__competed = False
        self.__is_ok = False
        self.__keys_file = None


    def is_completed(self):
        return self.__competed


    def is_ok(self):
        return self.__is_ok


    async def run(self):
        self.__competed = False
        self.__is_ok = False
        self.__keys_file = None

        output = []
        try:
            if self.__first_setup:
                output.append(self.__filter_result(await self._scratch_setup()))
                output.append(self.__filter_result(await self._server_setup()))

            output.append(self.__filter_result(await self._client_setup()))

            if self.__dl_keys:
                self.__keys_file = self._read_keys_file()

            self.__is_ok = True
            return output
        finally:
            self.__competed = True


    def keys_file_content(self):
        return self.__keys_file


    def __filter_result(self, rv):
        if rv[2] != 0:
            raise SubprocessError(rv)

        return rv


    def _read_keys_file(self):
        fn = osp.join(KEYS_BASE_DIR, self.__ip_addr, 'root', KEYS_FILE_NAME)
        try:
            with open(fn, 'rb') as f:
                content = f.read()

            os.remove(fn)
            return content
        except Exception as e:
            raise IOError(f'File i/o error [{fn}]') from e


    async def _scratch_setup(self):
        self.__scratch_setup_porcess = await asyncio.create_subprocess_shell(
            osp.join(self.__app_dir, 'vpn-setup/local/scratch-setup.sh') + f" '{self.__ip_addr}' {self.__ssh_password}",
            stdout=PIPE, stderr=PIPE
        )

        stdout, stderr = await self.__scratch_setup_porcess.communicate()
        return stdout.decode(), stderr.decode(), self.__scratch_setup_porcess.returncode


    async def _server_setup(self):
        self.__server_setup_porcess = await asyncio.create_subprocess_shell(
            osp.join(self.__app_dir, 'vpn-setup/local/server-setup.sh') + f" '{self.__ip_addr}' {self.__ssh_password}",
            stdout=PIPE, stderr=PIPE
        )

        stdout, stderr = await self.__server_setup_porcess.communicate()
        return stdout.decode(), stderr.decode(), self.__server_setup_porcess.returncode


    async def _client_setup(self):
        self.__client_setup_porcess = await asyncio.create_subprocess_shell(
            osp.join(self.__app_dir, 'vpn-setup/local/client-setup.sh') +
                f" '{self.__ip_addr}' {self.__ssh_password} '{self.__dl_keys}' '{self.__platform}'",
            stdout=PIPE, stderr=PIPE
        )

        stdout, stderr = await self.__client_setup_porcess.communicate()
        return stdout.decode(), stderr.decode(), self.__client_setup_porcess.returncode
