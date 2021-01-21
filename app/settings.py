from aux_stuff import make_key

EN_LOCALE = "en"
LOCALES = [EN_LOCALE]
DEFAULT_LOCALE = EN_LOCALE
SECRET_KEY = make_key() # for now no need to save something between reboots in case if, keys are stored in memory
KEYS_FILE_NAME = 'myvpn.zip'
KEYS_BASE_DIR = '/tmp/fetched'
LOG_DIR = './vpn41'



