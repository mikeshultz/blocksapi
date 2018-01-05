""" Handle user configuration 

Example
-------

    [default]
    dsn = postgresql://user:password@server.example.com/dbname
"""
import os
import sys
import logging
from configparser import ConfigParser

CONFIG = ConfigParser()

DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0
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
if not CONFIG['default'].get('dsn'):
    raise Exception("Invalid configuration")

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

DSN = CONFIG['default']['dsn']