""" Handle user configuration 

Example
-------

    [default]
    dsn = postgresql://user:password@server.example.com/dbname
    loglevel = INFO
    page_limit = 200
"""
import os
import sys
import logging
from configparser import ConfigParser

CONFIG = ConfigParser()

CONFIG_INI = 'blocksapi.ini'

user_conf = os.path.expanduser(os.path.join('~', '.config', CONFIG_INI))
if os.path.isfile(user_conf):
    CONFIG.read(user_conf)

sys_conf = os.path.expanduser(os.path.join('/etc', CONFIG_INI))
if os.path.isfile(sys_conf):
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

# Log level can be gotten from here: 
LEVEL = {
    'CRITICAL': 50,
    'ERROR':    40,
    'WARNING':  30,
    'INFO':     20,
    'DEBUG':    10
}
conf_loglevel = CONFIG['default'].get('loglevel')
logging.basicConfig(stream=sys.stdout, level=LEVEL.get(conf_loglevel, 'WARNING'))
LOGGER = logging.getLogger('blocks')

DEFAULT_LIMIT = CONFIG['default'].getint('page_limit', 500)
DEFAULT_OFFSET = 0
