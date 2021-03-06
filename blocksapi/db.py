""" Database models and utilities """
import logging
import decimal
import psycopg2
from datetime import datetime
from eth_utils.address import is_address
from rawl import RawlBase, RawlJSONEncoder
from .utils import results_hex_format, has_to_pg_varchar
from .config import LOGGER, DEFAULT_LIMIT, DEFAULT_OFFSET

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
        try:
            return super(JSONEncoder, self).default(o)
        except TypeError as e:
            if 'is not JSON' in str(e):
                return str(o)
            else:
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
            " WHERE block_timestamp BETWEEN {} AND {}",
            start, end)

        return (result[0][0], result[0][1])

    def get_range_date(self, start_time, end_time, limit=DEFAULT_LIMIT, 
                       offset=DEFAULT_OFFSET) -> list:
        """ Get a range of blocks between two numbers """

        if start_time > end_time:
            raise InvalidRange("start must come before end")

        return self.select(
            "SELECT {} FROM block"
            " WHERE block_timestamp BETWEEN {} AND {}"
            " ORDER BY block_number LIMIT {} OFFSET {}",
            self.columns, start_time, end_time, limit, offset)

    def get_range_number(self, start, end, limit=DEFAULT_LIMIT, 
                       offset=DEFAULT_OFFSET) -> list:
        """ Get a range of blocks between two numbers """

        if start > end:
            raise InvalidRange("start must come before end")

        return self.select(
            "SELECT {} FROM block"
            " WHERE block_number BETWEEN {} AND {}"
            " ORDER BY block_number LIMIT {} OFFSET {}",
           self.columns,  start, end, limit, offset)

    def get_latest(self) -> int:
        """ Get the latest block in the DB """

        res = self.query("SELECT MAX(block_number) FROM block;")
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
        # Deal with 'hash' column being in both tables
        self.aliased_columns = ['t.' + x for x in self.columns]

    def get_by_address(self, address:str, limit:int=DEFAULT_LIMIT,
                       offset:int=DEFAULT_OFFSET) -> list:
        """ Get a list of transactions for an address """

        if not is_address(address):
            raise ValueError("Address is invalid")

        result = self.select(
            "SELECT {} FROM transaction t JOIN block b USING (block_number)"
            " WHERE lower(from_address) = lower({})"
            " OR lower(to_address) = lower({})"
            " ORDER BY block_timestamp DESC LIMIT {} OFFSET {};",
            self.aliased_columns, address, address, limit, offset)

        result = results_hex_format(result, 'hash')

        return result

    def get_from(self, address:str, limit:int=DEFAULT_LIMIT,
                 offset:int=DEFAULT_OFFSET) -> list:
        """ Get a list of transactions for an address """

        if not is_address(address):
            raise ValueError("Address is invalid")

        result = self.select(
            "SELECT {} FROM transaction t JOIN block b USING (block_number)"
            " WHERE lower(from_address) = lower({})"
            " ORDER BY block_timestamp DESC LIMIT {} OFFSET {};",
            self.aliased_columns, address, limit, offset)

        result = results_hex_format(result, 'hash')

        return result

    def get_to(self, address:str, limit:int=DEFAULT_LIMIT,
                 offset:int=DEFAULT_OFFSET) -> list:
        """ Get a list of transactions for an address """

        if not is_address(address):
            raise ValueError("Address is invalid")

        result = self.select(
            "SELECT {} FROM transaction t JOIN block b USING (block_number)"
            " WHERE lower(to_address) = lower({})"
            " ORDER BY block_timestamp DESC LIMIT {} OFFSET {};",
            self.aliased_columns, address, limit, offset)

        result = results_hex_format(result, 'hash')

        return result

    def get_block(self, block_number:int, limit:int=DEFAULT_LIMIT,
                  offset:int=DEFAULT_OFFSET) -> list:
        """ Get transactions in a block """

        result = self.select(
            "SELECT {} FROM transaction t JOIN block b USING (block_number)"
            " WHERE block_number = {}"
            " ORDER BY block_timestamp DESC LIMIT {} OFFSET {};",
            self.aliased_columns, block_number, limit, offset)

        result = results_hex_format(result, 'hash')

        return result

    def get_count(self) -> int:
        """ Get the full count of transactions """

        res = self.query("SELECT COUNT(hash) FROM transaction;")
        if res is not None:
            return res[0][0]
        else:
            return 0

    def get_mean_gas_price(self, block_length) -> int:
        """ Get the mean gas price for the last X transactions """

        res = self.query(
            "WITH gas_prices AS "
            " (SELECT gas_price FROM transaction ORDER BY block_number DESC LIMIT {})"
            " SELECT MAX(gas_price), MIN(gas_price) FROM gas_prices;",
            block_length)
        if res is not None:
            return res[0][0] - res[0][1]
        else:
            return 0

    def get_average_gas_price(self, block_length) -> int:
        """ Get the average gas price for the last X transactions """

        res = self.query(
            "WITH gas_prices AS "
            " (SELECT gas_price FROM transaction ORDER BY block_number DESC LIMIT {})"
            " SELECT avg(gas_price) AS average FROM gas_prices;",
            block_length)
        if res is not None:
            return res[0][0]
        else:
            return 0
