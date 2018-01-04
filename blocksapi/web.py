from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
from .config import DSN
from .db import BlockModel, TransactionModel
from .validate import InvalidInput, beInteger, beHash

BLOCKS = BlockModel(DSN)
TRANSACTIONS = TransactionModel(DSN)


class JsonHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""
    def prepare(self):
        # Incorporate request JSON into arguments dictionary.
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                self.request.arguments.update(json_data)
            except json.JSONDecodeError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message) # Bad Request

        # Set up response dictionary.
        self.response = dict()

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error.'

        self.response = kwargs
        self.write_json()

    def write_json(self):
        output = json.dumps(self.response)
        self.write(output)


class MainHandler(JsonHandler):
    def get(self):
        self.redirect('https://gointo.software/')

class BlockHandler(JsonHandler):
    def get(self):

        # Single block request
        if self.request.arguments.get('block_number'):

            try:
                block_number = beInteger(self.request.arguments['block_number'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
            
            self.response['results'] = BLOCKS.get(block_number)

            self.write_json()

        # Block range request
        elif self.request.arguments.get('start') \
            and self.request.arguments.get('end'):

            try:
                start = beInteger(self.request.arguments['start'])
                end = beInteger(self.request.arguments['end'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
            
            self.response['results'] = BLOCKS.get_range_number(start, end)

            self.write_json()

        # Block range(date) request
        elif self.request.arguments.get('start_time') \
            and self.request.arguments.get('end_time'):

            try:
                start_time = beInteger(self.request.arguments['start_time'])
                end_time = beInteger(self.request.arguments['end_time'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))

            self.response['results'] = BLOCKS.get_range(start_time, end_time)

            self.write_json()

        else:
            self.write_error(400, message="Invalid request")


class TransactionHandler(JsonHandler):
    def get(self):
        
        # Single transaction request
        if self.request.arguments.get('hash'):

            try:
                tx_hash = beHash(self.request.arguments['hash'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
            
            self.response['results'] = TRANSACTIONS.get(tx_hash)

            self.write_json()

        # Transactions for a block
        elif self.request.arguments.get('block_number'):

            try:
                block_number = beInteger(self.request.arguments['block_number'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))
            
            self.response['results'] = TRANSACTIONS.get_block(block_number)

            self.write_json()

        # Transactions for an account
        elif self.request.arguments.get('from_address') \
            or self.request.arguments.get('to_address'):

            try:
                if self.request.arguments.get('from_address'):
                    from_address = beHash(self.request.arguments['from_address'])
                if self.request.arguments.get('to_address'):
                    to_address = beHash(self.request.arguments['to_address'])
            except InvalidInput as e:
                self.write_error(400, message=str(e))

            if from_address == to_address:
                self.response['results'] = TRANSACTIONS.get_address(to_address)
            else:
                if from_address:
                    self.response['results'].append(
                        TRANSACTIONS.get_from(from_address))

                if to_address:
                    self.response['results'].append(
                        TRANSACTIONS.get_to(to_address))

            self.write_json()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", MainHandler),
            (r"block/?", BlockHandler),
            (r"transaction/?", TransactionHandler),
        ]
        tornado.web.Application.__init__(self, handlers)

def main():
    app = Application()
    app.listen(8080)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()