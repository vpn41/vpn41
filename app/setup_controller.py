class SetupController:
    def __init__(self, setup_processors_pool):
        self.__pool = setup_processors_pool


    def setup(self, key, **params):
        self.__pool.spawn(key, **params)


    def status(self, key):
        p = self.__pool.get(key)
        if p is None:
            return dict(status='undefined')

        if not p.is_completed():
            return dict(status='pending')

        d = dict(status='completed', ok=p.is_ok())
        if p.keys_file_content() is not None:
            d['keys_file_url'] = '/keys/'

        return d


    def clear_status(self, key):
        self.__pool.clear(key)


    def keys_file_content(self, key):
        p = self.__pool.get(key)
        return p.keys_file_content() if p is not None else None
