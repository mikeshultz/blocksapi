import json
from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from eth_utils.address import is_address
from .config import DSN, DEFAULT_LIMIT, LOGGER
from .db import JSONEncoder, BlockModel, TransactionModel
from .validate import (
    InvalidInput,
    be_integer,
    be_hash,
    be_datetime,
    be_address,
    be_string,
)
from .utils import results_hex_format, has_to_pg_varchar
from .docs import JSON_SCHEMA
from .ratelimiter import IPLimiter

BLOCKS = BlockModel(DSN)
TRANSACTIONS = TransactionModel(DSN)
log = LOGGER.getChild('web')


class JsonHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""
    def __init__(self, *args, **kwargs):
        super(JsonHandler, self).__init__(*args, **kwargs)
        self.limiter = IPLimiter()
        
    def prepare(self):
        # Init the limiter if needed
        if not self.limiter:
            self.limiter = IPLimiter()
        # Handle rate limiting if the subsystem is available
        if self.limiter and self.request.remote_ip:
            allow = self.limiter.request(self.request.remote_ip)
            if not allow:
                log.warning("Request rate limited from {}".format(self.request.remote_ip))
                self.send_error(429, message="Request has been rate limited")
                return

        # Incorporate request JSON into arguments dictionary.
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                self.request.arguments.update(json_data)
            except json.JSONDecodeError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message) # Bad Request

        # Set up response dictionary.
        self.response = {}

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

    def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            kwargs['message'] = 'Unknown error.'
        if 'exc_info' in kwargs:
            print(kwargs.pop('exc_info'))

        self.set_status(status_code)
        self.response = kwargs
        self.write_json()

    def write_json(self):
        output = json.dumps(self.response, cls=JSONEncoder)
        self.write(output)


class MainHandler(JsonHandler):
    def get(self):
        self.response['endpoints'] = JSON_SCHEMA
        self.write_json()

class HealthHandler(JsonHandler):
    def get(self):
        max_block = BLOCKS.get_latest()
        self.response['message'] = 'ok'
        self.response['blockNumber'] = max_block
        self.write_json()

class BlockHandler(JsonHandler):
    def post(self):

        # Single block request
        if self.request.arguments.get('block_number'):

            try:
                block_number = be_integer(self.request.arguments['block_number'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return
            
            res = BLOCKS.get(block_number)

            if len(res) == 0:
                self.set_status(404)
            else:
                # Format the hash field properly
                res = results_hex_format(res, 'hash')

            self.response['page'] = 1
            self.response['pages'] = 1
            self.response['results'] = res

            self.write_json()

        # Block range request
        elif self.request.arguments.get('start') \
            and self.request.arguments.get('end'):

            try:
                start = be_integer(self.request.arguments['start'])
                end = be_integer(self.request.arguments['end'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return

            offset = 0
            if self.request.arguments.get('page'):
                try:
                    offset = int(self.request.arguments['page']) * DEFAULT_LIMIT
                except ValueError:
                    self.write_error(400, message="Invalid page")
                    return
            
            res = BLOCKS.get_range_number(start, end, offset=offset)

            if len(res) == 0:
                self.set_status(404)
            else:
                # Format the hash field properly
                res = results_hex_format(res, 'hash')

            self.response['page'] = self.request.arguments.get('page', 1)
            self.response['results'] = res

            self.write_json()

        # Block range(date) request
        elif self.request.arguments.get('start_time') \
            and self.request.arguments.get('end_time'):

            try:
                start_time = be_datetime(self.request.arguments['start_time'])
                end_time = be_datetime(self.request.arguments['end_time'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return

            offset = 0
            if self.request.arguments.get('page'):
                try:
                    offset = int(self.request.arguments['page']) * DEFAULT_LIMIT
                except ValueError:
                    self.write_error(400, message="Invalid page")
                    return

            res = BLOCKS.get_range_date(start_time, end_time, offset=offset)

            if len(res) == 0:
                self.set_status(404)
            else:
                # Format the hash field properly
                res = results_hex_format(res, 'hash')

            self.response['page'] = self.request.arguments.get('page', 1)
            self.response['results'] = res

            self.write_json()

        else:
            self.write_error(400, message="Invalid request")


class TransactionHandler(JsonHandler):
    def post(self):
        
        # Single transaction request
        if self.request.arguments.get('hash'):

            try:
                tx_hash = be_hash(self.request.arguments['hash'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return

            # Garbage due to weird storage in DB.  TODO Fix this
            if tx_hash[:2] == "0x":
                tx_hash = has_to_pg_varchar(tx_hash)
            
            res = TRANSACTIONS.get(tx_hash)

            if len(res) == 0:
                self.set_status(404)
            else:
                res = results_hex_format(res, 'hash')

            self.response['results'] = res

            self.write_json()

        # Transactions for a block
        elif self.request.arguments.get('block_number'):

            try:
                block_number = be_integer(self.request.arguments['block_number'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return

            offset = 0
            if self.request.arguments.get('page'):
                try:
                    offset = int(self.request.arguments['page']) * DEFAULT_LIMIT
                except ValueError:
                    self.write_error(400, message="Invalid page")
                    return
            
            res = TRANSACTIONS.get_block(block_number, offset=offset)

            if len(res) == 0:
                self.set_status(404)
            else:
                res = results_hex_format(res, 'hash')

            self.response['results'] = res

            self.write_json()

        # Transactions for an account
        elif self.request.arguments.get('from_address'):

            try:
                if self.request.arguments.get('from_address'):
                    from_address = be_address(self.request.arguments['from_address'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return

            offset = 0
            if self.request.arguments.get('page'):
                try:
                    offset = int(self.request.arguments['page']) * DEFAULT_LIMIT
                except ValueError:
                    self.write_error(400, message="Invalid page")
                    return

            res = TRANSACTIONS.get_from(from_address)

            if len(res) == 0:
                self.set_status(404)
            else:
                res = results_hex_format(res, 'hash')

            self.response['results'] = res

            self.write_json()

        # Transactions for an account
        elif self.request.arguments.get('to_address'):

            try:
                if self.request.arguments.get('to_address'):
                    to_address = be_address(self.request.arguments['to_address'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return

            offset = 0
            if self.request.arguments.get('page'):
                try:
                    offset = int(self.request.arguments['page']) * DEFAULT_LIMIT
                except ValueError:
                    self.write_error(400, message="Invalid page")
                    return

            res = TRANSACTIONS.get_to(to_address)

            if len(res) == 0:
                self.set_status(404)
            else:
                res = results_hex_format(res, 'hash')

            self.response['results'] = res

            self.write_json()

        # Transactions for an account
        elif self.request.arguments.get('address'):

            try:
                if self.request.arguments.get('address'):
                    address = be_address(self.request.arguments['address'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
                return

            offset = 0
            if self.request.arguments.get('page'):
                try:
                    offset = int(self.request.arguments['page']) * DEFAULT_LIMIT
                except ValueError:
                    self.write_error(400, message="Invalid page")
                    return

            res = TRANSACTIONS.get_by_address(address)

            if len(res) == 0:
                self.set_status(404)
            else:
                res = results_hex_format(res, 'hash')

            self.response['results'] = res

            self.write_json()


class GasPriceHandler(JsonHandler):
    def post(self):
        
        try:
            calc_type = be_string(self.request.arguments['type'])
        except InvalidInput as e:
            self.write_error(400, message=str(e))
            return

        try:
            block_length = be_integer(self.request.arguments.get('block_length'))
        except InvalidInput as e:
            block_length = 500

        if calc_type == 'mean':
            res = TRANSACTIONS.get_mean_gas_price(block_length)
        else:
            res = TRANSACTIONS.get_average_gas_price(block_length)

        self.response['results'] = int(res)

        self.write_json()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/block/?", BlockHandler),
            # Disabled until we have more data
            # (r"/gas-price/?", GasPriceHandler),
            # (r"/transaction/?", TransactionHandler),
            (r"/health/?", HealthHandler),
            (r"/?", MainHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

def main(port=8081):
    print("Starting server on port {}".format(port))
    app = Application()
    app.listen(port)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()