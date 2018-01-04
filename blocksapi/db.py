""" Database models and utilities """
import logging
import decimal
import psycopg2
from datetime import datetime
from rawl import RawlBase, RawlJSONEncoder
from .config import LOGGER

log = LOGGER.getChild('db')


class InvalidRange(IndexError): pass


class JSONEncoder(RawlJSONEncoder):
    """ 
    A JSON encoder that can convert python's Decimal
    """
    def default(self, o):
        if type(o) == decimal.Decimal:
            # This sucks, but is maybe the only way to know?
            if '.' in str(o):
                return float(o)
            else:
                return int(o)
        return super(JSONEncoder, self).default(o)


class BlockModel(RawlBase):
    def __init__(self, dsn: str):
        super(BlockModel, self).__init__(dsn, table_name='block', 
            columns=['block_number', 'block_timestamp', 'hash', 'miner', 
                     'nonce', 'difficulty', 'gas_used', 'gas_limit', 'size'], 
            pk_name='block_number')

    def get_range(self, start: datetime, end: datetime) -> tuple:
        """ Get a range of blocks from start to end """

        if start > end:
            raise InvalidRange("start must come before end")

        result = self.query(
            "SELECT MIN(block_no), MAX(block_no) FROM block"
            " WHERE block_time BETWEEN {} AND {}",
            start, end)

        return (result[0][0], result[0][1])

    def get_latest(self) -> int:
        """ Get the latest block in the DB """

        res = self.query("SELECT MAX(block_no) FROM block;")
        if res is not None:
            return res[0][0]
        else:
            return 0

class TransactionModel(RawlBase):
    def __init__(self, dsn: str):
        super(TransactionModel, self).__init__(dsn, table_name='transaction', 
            columns=['hash', 'block_number', 'from_address', 'to_address',
                     'value', 'gas_price', 'gas_limit', 'nonce', 'input'],
            pk_name='hash')

    def get_by_address(self, address: str) -> list:
        """ Get a list of transactions for an address """

        if not is_address(address):
            raise ValueError("Address is invalid")

        result = self.select(
            "SELECT {} FROM transaction"
            " WHERE from_address = {} OR to_address = {};",
            self.columns, address, address)

        return result

    def get_count(self) -> int:
        """ Get the full count of transactions """

        res = self.query("SELECT COUNT(hash) FROM transaction;")
        if res is not None:
            return res[0][0]
        else:
            return 0