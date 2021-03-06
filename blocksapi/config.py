""" Handle user configuration 

Example
-------

    [default]
    dsn = postgresql://user:password@server.example.com/dbname
    loglevel = INFO
    page_limit = 200
"""
import sys
import logging
from pathlib import Path
from configparser import ConfigParser

CONFIG = ConfigParser()

CONFIG_INI = 'blocksapi.ini'

user_conf = Path('~').joinpath('.config', CONFIG_INI).expanduser().resolve()
if user_conf.is_file():
    print('Loading configuration from {}.'.format(user_conf))
    CONFIG.read(user_conf)

sys_conf = Path('/etc').joinpath('blocksapi', CONFIG_INI)
if sys_conf.is_file():
    print('Loading configuration from {}.'.format(sys_conf))
    CONFIG.read(sys_conf)

if 'default' not in CONFIG:
    raise Exception("No configuration found")

# Validate
if CONFIG['default'].get('dsn'):
    DSN = CONFIG['default']['dsn']
else:
    if not CONFIG['postgresql'].get('user'):
        raise Exception("Missing database configuration")
        
    DSN = "postgresql://%s:%s@%s:%s/%s" % (
        CONFIG['postgresql']['user'],
        CONFIG['postgresql']['pass'],
        CONFIG['postgresql'].get('host', "localhost"),
        CONFIG['postgresql'].get('port', 5432),
        CONFIG['postgresql'].get('name', "blocks")
        )

try:
    REDIS = {
        "host": CONFIG['redis'].get('host', 'localhost'),
        "port": CONFIG['redis'].get('port', 6379),
        "password": CONFIG['redis'].get('password'),
    }
except KeyError:
    REDIS = {
        "host": 'localhost',
        "port": 6379,
        "password": None,
    }
RATE_LIMITER_EXPIRY = 300 # 5 minutes
RATE_LIMIT = RATE_LIMITER_EXPIRY # 1 request per second

# Log level can be gotten from here: 
LEVEL = {
    'CRITICAL': 50,
    'ERROR':    40,
    'WARNING':  30,
    'INFO':     20,
    'DEBUG':    10
}
conf_loglevel = CONFIG['default'].get('loglevel')
print("Log level {}".format(conf_loglevel))
logging.basicConfig(stream=sys.stdout, level=LEVEL.get(conf_loglevel, 'WARNING'))
LOGGER = logging.getLogger('blocks')
log = LOGGER.getChild('config')

DEFAULT_LIMIT = CONFIG['default'].getint('page_limit', 500)
DEFAULT_OFFSET = 0
